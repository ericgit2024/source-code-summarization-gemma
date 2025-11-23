import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os

class InferenceEngine:
    def __init__(self, base_model_name="google/gemma-2b-it", adapter_path=None, hf_token=None):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.base_model_name = base_model_name
        self.adapter_path = adapter_path
        self.hf_token = hf_token

    def load_model(self):
        print(f"Loading model {self.base_model_name} on {self.device}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name, token=self.hf_token)
            
            # Load base model
            # optimization: load in 4bit if cuda available
            if self.device == "cuda":
                from transformers import BitsAndBytesConfig
                quantization_config = BitsAndBytesConfig(load_in_4bit=True)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_name, 
                    quantization_config=quantization_config,
                    device_map="auto",
                    token=self.hf_token
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(self.base_model_name, token=self.hf_token)
                self.model.to(self.device)

            if self.adapter_path and os.path.exists(self.adapter_path):
                print(f"Loading adapter from {self.adapter_path}...")
                self.model = PeftModel.from_pretrained(self.model, self.adapter_path, token=self.hf_token)
            
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback for demo purposes if model loading fails (e.g. no internet/auth)
            self.model = None

    def generate(self, prompt, max_new_tokens=128):
        if not self.model:
            return "Error: Model not loaded or failed to load. Check logs."
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
            
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Post-processing to extract just the response if needed
        # The prompt template has "### Response:\n"
        if "### Response:" in generated_text:
            return generated_text.split("### Response:")[-1].strip()
        return generated_text
