import pandas as pd
from langchain_ollama import ChatOllama

# Initialize your local LLM (Ollama)
MODEL_NAME = "qwen2.5:3b"
llm = ChatOllama(model=MODEL_NAME, num_ctx=32000)

# 🤖 AI Insight Generator
def analyze_component_trends(df):
    summary = df.to_string(index=False)
    prompt = (
        "Analyze the following PC component listings from Ultrapc.ma and provide:\n"
        "- Insights on price ranges\n"
        "- Most popular brands\n"
        "- Availability insights (if applicable)\n"
        "- Categorization by component types\n"
        "- Top picks between 3000dh and 4000dh\n\n"
        f"{summary}\n\n"
        "AI Analysis:"
    )
    return llm.invoke(prompt)

# 📦 Load data from CSV or directly as a DataFrame
def run_analysis():
    try:
        df = pd.read_csv(r"C:\Users\ElMehdi\Documents\Projects\Python_Automation\AI_Agent\AI_Agent\components.csv")
    except FileNotFoundError:
        print("❌ File components.csv not found.")
        return

    analysis = analyze_component_trends(df)

    print("\n📊 AI-Generated Component Insights:\n")
    print(analysis)

# ✅ This is what you should have at the bottom — nothing else
if __name__ == "__main__":
    run_analysis()