import random

def main(query:str)->dict:
    """
    基于固定短语匹配的古诗搜索问答处理器
    
    Args:
        query: 用户输入的问题
        
    Returns:
        Dict: 包含回复类型、回复内容等信息的字典
    """
    # 去除首尾空格
    query = query.strip()

    # 打招呼相关的固定短语
    greeting_phrases = {
        # 基本问候
        "你好", "您好", "hi", "hello", "嗨", "哈喽", "哈罗",
        "早上好", "下午好", "晚上好", "上午好", "中午好", "晚安",
        "早", "午安", "good morning", "good afternoon", "good evening",
        # 询问身份
        "你是谁", "你是什么", "你叫什么", "你的名字", "介绍一下自己", 
        "自我介绍", "你是什么东西", "你是哪个", "你是啥",
        # 询问状态
        "你好吗", "怎么样", "还好吗", "你还好吗", "最近怎么样",
        "你在吗", "在不在", "还在吗", "在线吗", "你在线吗",
        # 询问能力
        "你能干什么", "你会做什么", "你能做什么", "你的功能", 
        "你有什么用", "你的作用", "你的职责", "你的用途",
        "你能帮我查什么", "你可以查什么", "你会查什么", "你懂古诗吗",
        "能力介绍", "功能介绍", "你的能力", "你有什么功能",
        # 开始对话
        "开始", "开始查诗", "开始搜索", "开始检索", "我想查诗",
        "我想找诗", "我想问古诗", "我想了解古诗", "检索一下",
        # 测试类
        "测试", "试试", "试一试", "test", "testing", "试试看",
        "测试一下", "看看", "检查一下"
    }
    
     # 固定回复
    greeting_response = "你好，很高兴为您服务！我是您的古诗搜索小助手，可以帮您按诗名、作者检索古诗。"
    # 礼貌用语
    thank_phrases = {
        "谢谢", "感谢", "多谢", "谢了", "thanks", "thank you", 
        "thx", "3q", "3x", "谢谢你", "感谢你", "多谢了",
        "非常感谢", "十分感谢", "万分感谢", "太感谢了"
    }
    
    goodbye_phrases = {
        "再见", "拜拜", "bye","byebye","goodbye", "88", "走了", "告辞",
        "先走了", "下次见", "回头见", "有空再聊", "改天聊",
        "see you", "拜", "溜了", "闪了", "slip away"
    }
    
        
    polite_responses = {
        "thank": [
            "不用客气，随时为您服务！", 
            "很高兴能帮助到您！", 
            "这是我应该做的，有问题随时找我哦！",
            "客气了，有什么问题尽管问！",
            "不客气，祝您读诗愉快！"
        ],
        "goodbye": [
            "再见！期待下次为您服务！", 
            "祝您生活愉快，有问题随时来找我！", 
            "再见！祝您读诗愉快！",
            "拜拜！有问题随时回来咨询！",
            "再见！祝您学习愉快！"
        ]
    }
    # 人工服务相关短语
    human_service_phrases = {
        # 直接要求人工服务
        "人工服务", "人工客服", "人工坐席", "人工咨询", "人工帮助",
        "人工支持", "人工答疑", "人工解答", "人工回复", "人工对话",
        # 转接相关
        "转人工", "找人工", "要人工", "转接人工", "转接客服",
        "切换人工", "接入人工", "联系人工", "答疑入口",
        # 真人服务
        "真人服务", "真人客服", "真人咨询", "真人对话", "真人帮助",
        "活人", "真人", "人类", "人工", "真的人",
        # 服务支持相关
        "客服", "在线客服", "联系客服", "找客服", "官方客服",
        "联系管理员", "找管理员", "系统管理员", "平台客服",
        # 老师/导师
        "联系老师", "找老师", "咨询老师", "请教老师", "老师帮忙",
        "专业老师", "指导老师", "古诗老师", "诗词老师",
        # 专业服务
        "专人服务", "专业咨询", "专业服务", "专家咨询",
        "顾问咨询", "一对一服务", "专属服务",
        # 反馈和问题
        "反馈问题", "意见反馈", "系统问题", "服务问题",
        "接口问题", "工具问题", "无法查询", "查询失败",
        # 不满意
        "不满意", "有问题", "出问题", "不行", "服务差",
        "回答不对", "答非所问", "听不懂", "不准确"
    }


    
    human_service_response = "同学，当前古诗搜索服务暂未接入人工答疑，请先输入诗名或作者进行检索。"
    
    def normalize_text(text: str) -> str:
        """标准化文本：去除标点符号，转换为小写"""
        import re
        # 保留中文、英文、数字，去除标点符号和空格
        cleaned = re.sub(r'[^\w\u4e00-\u9fff]', '', text.lower().strip())
        return cleaned
    
    def exact_match_check(query_text: str, phrase_set) -> bool:
        """精确匹配检查"""
        normalized_query = normalize_text(query_text)
        
        for phrase in phrase_set:
            normalized_phrase = normalize_text(phrase)
            if normalized_phrase == normalized_query:
                return True
        return False
    
    def contains_match_check(query_text: str, phrase_set) -> bool:
        """包含匹配检查（用于短查询中包含关键短语的情况）"""
        normalized_query = normalize_text(query_text)
        
        # 只有当查询很短时才使用包含匹配（避免误匹配）
        if len(normalized_query) <= 10:
            for phrase in phrase_set:
                normalized_phrase = normalize_text(phrase)
                if normalized_phrase in normalized_query or normalized_query in normalized_phrase:
                    return True
        return False
    
    # 处理输入
    query = query.strip()
    if not query:
        return {
            "type": "error",
            "response": "请输入您的问题。",
            "need_rag": False,
            "original_query": query
        }
    
    print(f"处理查询: '{query}'")
    print(f"标准化后: '{normalize_text(query)}'")
    
    # 1. 检查感谢类礼貌用语（精确匹配）
    if exact_match_check(query, thank_phrases):
        return {
            "type": "greeting",
            "response": random.choice(polite_responses["thank"]),
            "need_rag": False,
            "original_query": query
        }
    
    # 2. 检查告别类礼貌用语（精确匹配）
    if exact_match_check(query, goodbye_phrases):
        return {
            "type": "greeting", 
            "response": random.choice(polite_responses["goodbye"]),
            "need_rag": False,
            "original_query": query
        }
    
    # 3. 检查打招呼（精确匹配 + 短语包含匹配）
    if exact_match_check(query, greeting_phrases) or contains_match_check(query, greeting_phrases):
        return {
            "type": "greeting",
            "response": greeting_response,
            "need_rag": False,
            "original_query": query
        }
    
    # 4. 检查人工服务请求（精确匹配 + 短语包含匹配）
    if exact_match_check(query, human_service_phrases) or contains_match_check(query, human_service_phrases):
        return {
            "type": "human_service",
            "response": human_service_response,
            "need_rag": False,
            "original_query": query
        }
    
    # 5. 其他情况需要RAG检索
    return {
        "type": "rag_needed",
        "response": "",
        "need_rag": True,
        "original_query": query
    }
