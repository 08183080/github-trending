import os
from zhipuai import ZhipuAI

path = 'D:\\github trending\\2024-09-28.txt'

def get_ai_analysis(path):
    client = ZhipuAI(api_key=os.environ.get("ZHIPUAI_API_KEY"))
    def get_trends(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    trends = get_trends(path)
    # print(trends)

    response = client.chat.completions.create(
        model="glm-4-flash",  # 填写需要调用的模型编码
        messages=[
            {"role": "system", "content": "你是一个 github trends 分析专家。负责分析 github 每日 python 项目的趋势。将英文介绍翻译成中文。输出整齐精致。接着在下一行，安利一个最惊艳的项目。再换一行，最后总结今天的趋势项目关注的领域和特点。语言保持简洁。"},
            {"role": "user", "content":f'{trends}' }
        ],
    )

    ans = response.choices[0].message.content
    # print(ans)
    return ans

ans = get_ai_analysis(path)

with open('D:\\github trending\\2024-09-28-ai.txt', 'w', encoding='utf-8') as f:
    f.write(ans)