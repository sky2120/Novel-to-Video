import os
import json
import requests

def read_novel(file_path):
    """读取小说文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

def call_moonshot_api(novel_content, api_key):
    """调用Moonshot AI API获取分镜Prompt模板和角色锁定参数"""
    endpoint = "https://api.moonshot.cn/v1/chat/completions"
    
    # 系统提示词
    system_prompt = """你是一个专业的漫画分镜设计师，擅长将小说文本转换为漫画分镜。请根据提供的小说内容，分析并输出以下内容：
    
1. 分镜Prompt模板：为每个关键场景生成适合AI图像生成的Prompt模板，包含场景描述、构图、光影、氛围等要素。
2. 角色锁定参数：提取并锁定主要角色的特征，包括外貌、服装、发型、表情等，确保在不同分镜中角色形象保持一致。

输出格式要求：
{
    "storyboard_prompts": [
        {
            "scene": "场景描述",
            "prompt": "详细的图像生成Prompt模板"
        }
    ],
    "character_locks": [
        {
            "name": "角色名称",
            "description": "角色详细描述",
            "features": {
                "appearance": "外貌特征",
                "clothing": "服装描述",
                "hairstyle": "发型描述",
                "expression": "表情特征",
                "other": "其他特征"
            }
        }
    ]
}

请确保输出的JSON格式正确，不包含任何额外的解释性文字。"""
    
    # 用户提示词
    user_prompt = f"""请分析以下小说内容，为其生成分镜Prompt模板和角色锁定参数：

{novel_content}"""
    
    # 构建请求体
    payload = {
        "model": "kimi-k2.5",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "max_tokens": 2000
    }
    
    # 发送请求
    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps(payload)
        )
        
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return None

def save_result(result, output_path):
    """保存结果到文件"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {output_path}")
    except Exception as e:
        print(f"保存文件失败: {e}")

def main():
    # 配置
    novel_file = "d:\\桌面\\临时文件\\A自动生成类型文件\\AI漫剧\\novel\\第一章.txt"
    output_file = "d:\\桌面\\临时文件\\A自动生成类型文件\\AI漫剧\\storyboard_result.json"
    api_key_file = "d:\\桌面\\临时文件\\A自动生成类型文件\\AI漫剧\\kimi api_key.txt"
    
    # 获取API密钥（从文件读取）
    api_key = os.environ.get("MOONSHOT_API_KEY")
    if not api_key:
        try:
            with open(api_key_file, 'r', encoding='utf-8') as f:
                api_key = f.read().strip()
            print("已从文件读取API密钥")
        except Exception as e:
            print(f"读取API密钥文件失败: {e}")
            api_key = input("请输入Moonshot API密钥: ")
    
    # 读取小说内容
    novel_content = read_novel(novel_file)
    if not novel_content:
        return
    
    # 调用API
    print("正在调用AI API分析小说...")
    result = call_moonshot_api(novel_content, api_key)
    
    if result:
        # 提取AI回复内容
        if "choices" in result and result["choices"]:
            ai_response = result["choices"][0]["message"]["content"]
            print("\nAI回复内容:")
            print(ai_response)
            
            # 尝试解析JSON
            try:
                parsed_result = json.loads(ai_response)
                save_result(parsed_result, output_file)
            except json.JSONDecodeError:
                print("AI回复不是有效的JSON格式，已保存原始回复")
                save_result({"raw_response": ai_response}, output_file)
        else:
            print("API返回格式异常")
            save_result(result, output_file)

if __name__ == "__main__":
    main()
