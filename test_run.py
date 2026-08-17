from llm.response_generator import ResponseGenerator

# This check ensures the code runs only when the script is executed directly
if __name__ == '__main__':
    print("Initializing the e-commerce chatbot...")
    # This will create an instance of your ResponseGenerator class,
    # which in turn initializes the RetrievalService and the LLM.
    chatbot = ResponseGenerator()

    # --- DEFINE YOUR QUERY HERE ---
    # You can switch between these queries to test the router logic.
    
    # This query should use the "Product Summaries" vector store
    query = "Does the Microsoft Surface Pro 4 Type Cover have a fingerprint reader?"
    
    # This query should use the "Reviews" vector store
    # query = "What did customers think about the sound quality of the Sony SRS-XB3 speakers?"

    print(f"\\nSending query to chatbot: '{query}'")
    
    # Generate an answer
    result = chatbot.generate_answer(query)

    # Print the results in a clean format
    print("\\n" + "="*50)
    print(f"QUERY: {query}")
    print(f"SOURCE KNOWLEDGE BASE: {result['source_store']}")
    print(f"\\nASTRO'S RESPONSE:")
    print(result['answer'])
    print("="*50)