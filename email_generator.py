from dotenv import load_dotenv
import os
from langchain.document_loaders import UnstructuredURLLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from gmail import gmail_create_draft

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


def get_company_page(url):
    print(url)
    loader = UnstructuredURLLoader(urls=[url])
    return loader.load()


def generate_email():
    # Get the data of the company you're interested in
    data = get_company_page('https://www.ycombinator.com/companies/doordash')
    print (data)

    print(f"You have {len(data)} document(s)")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=1)

    docs = text_splitter.split_documents(data)

    print(f"You now have {len(docs)} documents")

    map_prompt = """Below is a section of a website about {prospect}

    Write a concise summary about {prospect}. If the information is not about {prospect}, exclude it from your summary.

    {text}

    CONCISE SUMMARY:"""
    map_prompt_template = PromptTemplate(
        template=map_prompt, input_variables=["text", "prospect"]
    )

    combine_prompt = """
    Your goal is to write a personalized outbound email from {sales_rep}, a sales to {prospect}.

    A good email is personalized and include how we can help each other. We are a tech start up running AI integrations and large language models.
    Be sure to use value selling: A sales methodology that focuses on how your product or service will provide value to the customer instead of focusing on price or solution.

    INFORMATION ABOUT {prospect}:
    {text}

    INCLUDE THE FOLLOWING PIECES IN YOUR RESPONSE:
    - Start the email with the sentence: "We love that {prospect} helps teams..." then insert what they help teams do.
    - The sentence: "We can help you do XYZ by ABC" Replace XYZ with what {prospect} does and ABC with possible AI solutions.
    - A 1-3 sentence description about the {prospect}'s company
    - End your email with a call-to-action such as asking them to set up time to talk more.

    YOUR RESPONSE:
    """
    combine_prompt_template = PromptTemplate(
        template=combine_prompt, input_variables=["sales_rep", "prospect", "text"]
    )

    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)

    chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        map_prompt=map_prompt_template,
        combine_prompt=combine_prompt_template,
        verbose=True,
    )

    output = chain(
        {
            "input_documents": docs,
            "sales_rep": "Richard Porteous",
            "prospect": input("Prospect name: "),
        }
    )

    print(output["output_text"])

    # Save the output to a file
    with open("./docs/output.txt", "a") as f:
        f.write(output["output_text"])
    result = gmail_create_draft()
    print(result)
    return result
    # module for iteration
    # for i, company in df_companies.iterrows():
    #    print (f"{i + 1}. {company['Name']}")
    #    page_data = get_company_page(company['Link'])
    #    docs = text_splitter.split_documents(page_data)

    #    output = chain({"input_documents": docs, \
    #                "company":"RapidRoad", \
    #                "sales_rep" : "Greg", \
    #                "prospect" : company['Name'],
    #                "company_information" : company_information
    #               })

    #    print (output['output_text'])
    #    print ("\n\n")
