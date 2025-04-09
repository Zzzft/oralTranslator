# %%
'''
Requirements: pip install nltk rouge-score pyter3
'''
import nltk
import jieba
#import pyter # 计算ter
from tqdm import tqdm
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer
from rouge_chinese import Rouge
from nltk.translate.bleu_score import corpus_bleu, SmoothingFunction
import sacrebleu  # 更标准的 BLEU 实现
import string, re

# 标点过滤
def remove_punctuation(text):
    punc = '！？。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏' + string.punctuation
    return re.sub(r'[{}]+'.format(re.escape(punc)), '', text)

    
def calculate_bleu_scores(references, generated, intensive):
    """
    ### 标点过滤
    if intensive:
        generated = remove_punctuation(generated)
        references = [[remove_punctuation(ref) for ref in ref_group] 
                     for ref_group in references]
    """
    
    """
    计算 BLEU-1 到 BLEU-4 分数
    - `param` `reference_tokens`: 参考文本 (列表格式，包含多个参考句子)
    - `param` `generated_tokens`: 生成文本 (字符串格式)
    :return: BLEU-1 到 BLEU-4 分数
    """
    if intensive:
        # 中文分词处理
        generated = ' '.join(jieba.cut(generated.replace(" ", "")))
        print(generated)
        references = [[' '.join(jieba.cut(ref.replace(" ", ""))) for ref in ref_group] 
                    for ref_group in references]
        print(references)
        print("------------------")
    else:
        # 英文按空格分词
        generated = generated.split()
        references = [[ref.split() for ref in ref_group] for ref_group in references]

    # 使用 sacrebleu 计算 bleu-4
    bleu = sacrebleu.corpus_bleu([generated], references, tokenize="zh")
    sacre_bleu = bleu.score / 100  # sacrebleu 返回百分比值

    # 使用 NLTK 的 corpus_bleu 计算 bleu-n
    # 使用SmoothingFunction来避免BLEU为0的情况
    smoothing = SmoothingFunction().method1
    weights = [
        (1, 0, 0, 0),    # BLEU-1
        (0.5, 0.5, 0, 0), # BLEU-2
        (0.33, 0.33, 0.33, 0), # BLEU-3
        (0.25, 0.25, 0.25, 0.25) # BLEU-4
    ]
    bleu_scores = [
        sentence_bleu(references[0], generated, weights=w, smoothing_function=smoothing)
        for w in weights
    ]
    return bleu_scores + [sacre_bleu]
    
    
    # BLEU-1 到 BLEU-4
    #bleu_1 = sentence_bleu(reference_tokens, generated_tokens, weights=(1, 0, 0, 0), smoothing_function=smoothing_function)
    #bleu_2 = sentence_bleu(reference_tokens, generated_tokens, weights=(0.5, 0.5, 0, 0), smoothing_function=smoothing_function)
    #bleu_3 = sentence_bleu(reference_tokens, generated_tokens, weights=(0.33, 0.33, 0.33, 0), smoothing_function=smoothing_function)
    #bleu_4 = sentence_bleu(reference_tokens, generated_tokens, weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=smoothing_function)
    
    #return bleu_1, bleu_2, bleu_3, bleu_4

def calculate_rouge_scores(reference, generated):
    """
    计算 ROUGE-1, ROUGE-2, ROUGE-L 分数
    - `param` `reference`: 参考文本 (字符串格式)
    - `param` `generated`: 生成文本 (字符串格式)
    :return: 各类 ROUGE 分数
    """
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, generated)
    
    return scores['rouge1'].fmeasure, scores['rouge2'].fmeasure, scores['rougeL'].fmeasure

def calculate_meteor_score(reference_tokens, generated_tokens):
    """
    计算 METEOR 分数
    - `param` `reference_tokens`: 参考文本 (字符串格式)
    - `param` `generated_tokens`: 生成文本 (字符串格式)
    :return: METEOR 分数
    """
    reference_tokens = [[str(i) for i in tokens] for tokens in reference_tokens]
    generated_tokens = [str(i) for i in generated_tokens]
    return meteor_score(reference_tokens, generated_tokens)

def evaluate_all_metrics(tokenizer, reference, generated, intensive=False):
    """
    计算 BLEU-1 到 BLEU-4, ROUGE-1 到 ROUGE-4, METEOR分数
    - `param` `tokenizer`: 分词器
    - `param` `reference`: 参考文本 (列表格式，包含多个参考句子)
    - `param` `generated`: 生成文本 (字符串格式)
    - `param` `intensive`: 是否为字符密集型语言 (例如中文)
    :return: 各类指标的分数
    """
    #reference_tokens = tokenizer(reference)['input_ids']  # 分词
    #generated_tokens = tokenizer(generated)['input_ids']  # 分词
    if intensive:
        reference_intensive = " ".join(jieba.cut(reference[0].replace(" ", "")))
        generated_intensive = " ".join(jieba.cut(generated.replace(" ", "")))
        #reference_words = list(jieba.cut(reference[0]))
        #generated_words = list(jieba.cut(generated))
        #reference_intensive = ' '.join(reference_intensive)
        #generated_intensive = ' '.join(generated_intensive)
    else:
        reference_intensive = reference[0]
        generated_intensive = generated
    # 计算 BLEU 分数
    #bleu_1, bleu_2, bleu_3, bleu_4 = calculate_bleu_scores(reference_intensive.split(' '), generated_intensive.split(' '))
    bleu_1, bleu_2, bleu_3, bleu_4, sacrebleu = calculate_bleu_scores([reference], generated, intensive)
    
    # 计算 ROUGE 分数 (假设第一个参考句子为基准)
    if intensive:
        rouge = Rouge(metrics=["rouge-1", "rouge-2", "rouge-l"])
        scores = rouge.get_scores(generated_intensive, reference_intensive)
        rouge_1 = scores[0]['rouge-1']['f']
        rouge_2 = scores[0]['rouge-2']['f']
        rouge_l = scores[0]['rouge-l']['f']
    else:
        rouge_1, rouge_2, rouge_l = calculate_rouge_scores(reference_intensive, generated_intensive)
    
    # 计算 METEOR 分数
    meteor = calculate_meteor_score(reference, generated)
    #meteor = meteor_score([' '.join(ref) for ref in ref_words], ' '.join(gen_words))
    
    return {
        'BLEU-1': bleu_1,
        'BLEU-2': bleu_2,
        'BLEU-3': bleu_3,
        'BLEU-4': bleu_4,
        "sacreBLEU": sacrebleu,
        'ROUGE-1': rouge_1,
        'ROUGE-2': rouge_2,
        'ROUGE-L': rouge_l,
        'METEOR': meteor
    }

def evaluate_generation(tokenizer, predictions, references, intensive=False, print_table=True):
    """
    计算 BLEU-1 到 BLEU-4, ROUGE-1 到 ROUGE-4, METEOR 和 TER 分数
    - `param` `tokenizer`: 分词器
    - `param` `predictions`: 生成文本 (字符串格式)
    - `param` `references`: 参考文本 (列表格式，包含多个参考句子)
    - `param` `intensive`: 是否为字符密集型语言 (例如中文)
    - `param` `print_table`: 是否打印表格
    :return: 各类指标的分数
    """
    results = {
        'BLEU-1': 0,
        'BLEU-2': 0,
        'BLEU-3': 0,
        'BLEU-4': 0,
        'sacreBLEU': 0,
        'ROUGE-1': 0,
        'ROUGE-2': 0,
        'ROUGE-L': 0,
        'METEOR': 0,
        #'TER': 0
    }
    for pred, ref in tqdm(zip(predictions, references), total=len(references)):
        scores = evaluate_all_metrics(tokenizer, ref, pred, intensive)
        for metric, score in scores.items():
            results[metric] += score
    for metric in results:
        results[metric] /= len(references)
    
    if print_table:
        from prettytable import PrettyTable
        table = PrettyTable()

        table.field_names = ["Metric"] + [metric for metric in results.keys()]
        table.add_row(["Scores"] + [round(score, 4) for score in results.values()])
        
        # 打印表格
        print(table)
    return results
