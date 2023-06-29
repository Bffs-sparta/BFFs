from decouple import config
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AiChatBot
from .serializers import AiChatBotSerailizer

import openai

openai.api_key = config("OPENAI_API_KEY")


def send_text(request, user_input, ai_chat):
    gpt_prompt: list[dict] = []
    gpt_prompt.append(
        {
            # 시스템 역할(기본설정) 주기
            "role": "system",
            "content": "Response Korean!!!, Shortly. Chat naturally, friendly like talking to Bestie. Use half words",
        }
    )

    gpt_prompt.append(
        {
            # user_input을 넣어준다!
            "role": "user",
            "content": user_input,
        }
    )

    gpt_prompt.append(
        {
            "role": "assistant",
            "content": f"{ai_chat}"[:50],
        }
    )

    # with st.spinner("잠깐만! 생각 중이야!"):
    prompt = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=300,
        messages=gpt_prompt,
        temperature=0.8,
        top_p=1,
        presence_penalty=1,
    )
    # json response에서 필요한 부분만 불러옴

    return prompt["choices"][0]["message"]["content"]


class SendTextView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_chat = AiChatBot.objects.filter(user=request.user).last()
        hello_text = "안녕! 만나서 반가워:D"
        second_hello_text = "안녕! 다시 만나서 반가워:D"
        if not user_chat:
            return Response({"ai": hello_text}, status=200)
        else:
            return Response({"ai": second_hello_text}, status=200)

    def post(self, request):
        user_input = request.data["user_input"]
        user_chat = AiChatBot.objects.filter(user=request.user).last()
        if not user_chat:
            hello_text = "안녕! 만나서 반가워:D"
            response = send_text(request, user_input, hello_text)
        elif not user_chat.ai_text:
            second_hello_text = "안녕! 다시 만나서 반가워:D"
            response = send_text(request, user_input, second_hello_text)
        else:
            response = send_text(request, user_input, user_chat.ai_text[0])

        # 유저 데이터에 저장 및 채팅 내용 저장해주기
        if not user_chat:
            chat = AiChatBot.objects.create(
                user=request.user,
                user_text=[user_input],
                ai_text=[response, hello_text],
            )
            serializer = AiChatBotSerailizer(chat, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"ai": response}, status=200)
        elif not user_chat.ai_text:
            chat = AiChatBot.objects.update(
                user=request.user,
                user_text=[user_input],
                ai_text=[response, second_hello_text],
            )
            serializer = AiChatBotSerailizer(chat, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"ai": response}, status=200)
        else:
            user_chat.user_text.insert(0, user_input)
            user_chat.ai_text.insert(0, response)
            new_data_set = {
                "user_text": user_chat.user_text[:10],
                "ai_text": user_chat.ai_text[:10],
            }
            serializer = AiChatBotSerailizer(user_chat, data=new_data_set)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)

            return Response({"ai": response}, status=200)
