import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from langchain_ollama import ChatOllama

# LangChain model setup
MODEL_NAME = "qwen2.5:3b"
llm = ChatOllama(model=MODEL_NAME, num_ctx=32000)

# Clean price column
def clean_price(df):
    df["Price (DH)"] = (
        df["Price"]
        .str.replace("DH", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.extract(r"(\d+(?:\.\d+)?)")[0]
        .astype(float)
    )
    return df

# AI analysis
def analyze_component_trends(df):
    summary = df.to_string(index=False)
    prompt = (
        f"Analyze the following PC component listings from Ultrapc.ma and provide insights on price ranges, popular brands, availability, and types of components. "
        f"Also, suggest which components are good deals within a price range of 3000dh to 4000dh:\n\n{summary}\n\nAI Analysis:"
    )
    return llm.invoke(prompt)

if __name__ == "__main__":
    main()