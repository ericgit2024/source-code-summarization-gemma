import evaluate

class MetricsCalculator:
    def __init__(self):
        self.bleu = evaluate.load("bleu")
        self.rouge = evaluate.load("rouge")
        self.meteor = evaluate.load("meteor")
        self.bertscore = evaluate.load("bertscore")

    def calculate_metrics(self, predictions, references):
        """
        predictions: list of strings
        references: list of strings
        """
        results = {}
        
        # BLEU
        bleu_score = self.bleu.compute(predictions=predictions, references=references)
        results['bleu'] = bleu_score['bleu']
        
        # ROUGE
        rouge_score = self.rouge.compute(predictions=predictions, references=references)
        results['rouge1'] = rouge_score['rouge1']
        results['rouge2'] = rouge_score['rouge2']
        results['rougeL'] = rouge_score['rougeL']
        
        # METEOR
        meteor_score = self.meteor.compute(predictions=predictions, references=references)
        results['meteor'] = meteor_score['meteor']
        
        # BERTScore
        # Warning: This can be slow and memory intensive
        try:
            bert_score = self.bertscore.compute(predictions=predictions, references=references, lang="en")
            results['bertscore_f1'] = sum(bert_score['f1']) / len(bert_score['f1'])
        except Exception as e:
            print(f"BERTScore calculation failed: {e}")
            results['bertscore_f1'] = 0.0
            
        return results
