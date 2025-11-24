import os
from zai import ZhipuAiClient


def load_knowledge_base(knowledge_file: str = "../docs/writing_style_knowledge.txt") -> str:
    """
    加载写作风格知识库
    
    Args:
        knowledge_file: 知识库文件路径，默认为当前目录下的 writing_style_knowledge.txt
    
    Returns:
        知识库内容字符串，如果文件不存在则返回空字符串
    """
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    knowledge_path = os.path.join(current_dir, knowledge_file)
    
    try:
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def rewrite_paper_paragraph(
    paragraph: str,
    api_key: str = "88ad5bec19b1464689a267feaa706bc0.Xsn6EZKEG1mt2zNp",
    model: str = "glm-4.5-flash",
    temperature: float = 0.5,
    use_knowledge_base: bool = True
) -> str:
    """
    对论文段落进行改写，降低 AIGC 率
    
    Args:
        paragraph: 需要改写的论文段落文本
        api_key: 智谱 AI API 密钥
        model: 使用的模型名称，默认为 glm-4.5-flash
        temperature: 控制输出随机性，范围 0-1，默认 0.5
        use_knowledge_base: 是否使用知识库提供额外参考，默认 True
    
    Returns:
        改写后的论文段落文本
    """
    # 参数验证
    if not paragraph or not paragraph.strip():
        raise ValueError("输入的论文段落不能为空")
    
    # 初始化客户端
    client = ZhipuAiClient(api_key=api_key)
    
    # 构建提示词
    prompt = f"""一、角色：一名普通的大学四年级学生
二、任务：对论文段落重新编写，使段落表达更贴近自然表述
三、编写要求：
1. 可删减冗余连接词，将部分书面化连接词替换为更口语化的简单表述，允许适当重复核心名词；
2. 采用更灵活的句式结构，可拆分长句、调整短语顺序，使用更通俗的动词表达；
3. 调整功能描述的呈现方式，可将并列功能用更具层次感的表述拆分，允许适当添加补充性表述；
4. 避免使用复杂长句，采用短句组合，不添加 "我" 等人称，可用 "本文" 替代；
5. 确保核心信息不遗漏；
6. 需要保持一定的学术风格。
四、输出要求：只需要输出重写之后的论文段落，不要输出任何其他内容。"""
    
    # 如果启用知识库，添加知识库内容作为参考
    if use_knowledge_base:
        knowledge_content = load_knowledge_base()
        if knowledge_content:
            prompt += f"\n\n五、写作风格参考（AI风格转人类风格示例）：\n{knowledge_content}"
            prompt += f"\n\n六、需要重新编写的论文段落如下：\n'''{paragraph}'''"
        else:
            prompt += f"\n\n五、需要重新编写的论文段落如下：\n'''{paragraph}'''"
    else:
        prompt += f"\n\n五、需要重新编写的论文段落如下：\n'''{paragraph}'''"
    
    try:
        # 调用 API 进行改写
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            thinking={
                "type": "disabled",  # 禁用深度思考模式加快响应
            },
            stream=False,
            max_tokens=96000,
            temperature=temperature
        )
        
        # 提取改写后的内容
        rewritten_text = response.choices[0].message.content.strip()
        
        # 清理可能的多余标记
        if rewritten_text.startswith("'''") and rewritten_text.endswith("'''"):
            rewritten_text = rewritten_text[3:-3].strip()
        elif rewritten_text.startswith('"""') and rewritten_text.endswith('"""'):
            rewritten_text = rewritten_text[3:-3].strip()
        elif rewritten_text.startswith('"') and rewritten_text.endswith('"'):
            rewritten_text = rewritten_text[1:-1].strip()
        
        return rewritten_text
    
    except Exception as e:
        raise Exception(f"论文段落改写失败: {str(e)}")


# 使用示例
if __name__ == "__main__":
    # 测试用例
    test_paragraph = """
    本系统通过采用先进的深度学习算法，结合多种自然语言处理技术手段，
    实现了对文本数据的高效处理与分析。该方法不仅能够显著提高文本分类的准确率，
    而且可以有效降低计算复杂度，从而实现更好的整体性能表现。
    """
    
    print("原始段落:")
    print(test_paragraph.strip())
    print("\n" + "="*50 + "\n")
    
    try:
        rewritten = rewrite_paper_paragraph(test_paragraph)
        print("改写后段落:")
        print(rewritten)
    except Exception as e:
        print(f"错误: {e}")