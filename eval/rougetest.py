from rouge import Rouge
import jieba # you can use any other word cutting library

hypothesis = "从我成年到结婚，再到如今有了孙女，始终与母亲共同生活。"
hypothesis = ' '.join(jieba.cut(hypothesis)) 

reference = "我一直跟着母亲在一起生活，从我出生就没离开母亲。"
reference = ' '.join(jieba.cut(reference))

rouge = Rouge()
scores = rouge.get_scores(hypothesis, reference)

print(scores);