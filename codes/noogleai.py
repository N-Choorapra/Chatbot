from openai import OpenAI
from dotenv import load_dotenv
from configparser import ConfigParser
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import selenium, time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import re
from langchain_experimental.text_splitter import SemanticChunker
from langchain.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv("../Utils/.env")


class NoogleAI(OpenAI):
    def __init__(self, audioForm = None, text_instruction = None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        if audioForm is None and text_instruction is None:
            raise ValueError("Please provide either the Audio or Text")
        self.audioForm = audioForm
        self.textInstruction = text_instruction
        self.config = ConfigParser()
        self.config.read("../Utils/config.ini")
        print("here here", self.textInstruction)
        
    def transcribe(self):
        print("inside transcription",)
        print(self.audioForm)
        transcription = self.audio.transcriptions.create(
                model = self.config.get("transcription", "modelName"),
                file  = self.audioForm
                )
        print("---transcription completed---")
        return transcription.text
    
    def convertSearchParams(self):
        
        if self.audioForm:
            instruction = self.transcribe()
        elif self.textInstruction:
            instruction = self.textInstruction
        response = self.chat.completions.create(model=self.config.get("summarization", "searchModel"),
                                                messages=[{"role":"system", "content":"You are an AI assistant who can convert the given input text to a well strucured single set of DuckDuckGo search parameters. Do not produce keywords of definite values, ie the ones in double quotes. Remove if anything generated with double quotes and give the actual value of input. Add this site:tfoco.com along with the other search parameters to ensure the search gives results from the website tfoco.com"},
                                                          {"role":"user", "content":"The input from a user query is given here: {}".format(instruction)}],#
                                                temperature=self.config.getfloat("summarization", "temperature"),
                                                seed=1
                                                )
        print("---parameter generation completed---")
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    
    async def summarizeResults(self, driver : selenium.webdriver.chrome.webdriver.WebDriver):
        instruction = self.convertSearchParams()
        text, sources = await NoogleExtractor().textExtractor(instruction, driver)
        text_splitter = SemanticChunker(OpenAIEmbeddings())
        docs = text_splitter.create_documents(text)
        db = FAISS.from_documents(docs, OpenAIEmbeddings())
        retriever = db.as_retriever()
        docs = retriever.invoke(instruction)
        texts = [doc.page_content for doc in docs[:2]]
        
        response = self.chat.completions.create(model=self.config.get("summarization", "summarizeModel"),
                                                messages=[{"role":"system", "content":f"You are an expert in summarizing the given content and answer user question based on the given content. The target is to summarize the content such that, it'd highlight the services The Family Office Company BSC, Bahrain, a wealth management company can benefit from. The context: {str(texts)}"},
                                                          {"role":"user", "content": f"User: {self.textInstruction}"}],
                                                temperature=self.config.getfloat("summarization", "temperature"),
                                                seed=1,
                                                )
        print("---summarization completed---")
        return response.choices[0].message.content, sources
    
    
    
class NoogleExtractor:
    
    def fetchWeb(self, searchParams, driver):
        driver.get("https://duckduckgo.com/")
        time.sleep(2)
        
        searchBox = driver.find_element(By.XPATH, '//input[@aria-label="Search with DuckDuckGo"]')
        searchBox.send_keys(searchParams)
        searchBox.send_keys(Keys.ENTER)
        driver.save_screenshot("image.png")
        searchResults = driver.find_elements(By.XPATH, '//li[@data-layout="organic"]//*[@data-testid="result-title-a"]')
        searchResults = [result.get_attribute("href") for result in searchResults]
        
        return searchResults[:2]
    
    async def fetchUrl(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()
            
    async def fetchMultipleUrls(self, urls):
        print(urls)
        tasks = []
        results = []
        # Create a semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(4)  # Change the number to control concurrency

        async def fetchWithSemaphore(url):
            nonlocal results
            async with semaphore:
                result = await self.fetchUrl(url)
                results.append({"result":result, "source":url})

        # Create tasks for each URL
        for url in urls:
            task = asyncio.ensure_future(fetchWithSemaphore(url))
            tasks.append(task)

        # Gather all tasks
        await asyncio.gather(*tasks)

        return results
    
    async def resultExtract(self, searchParams, driver):
        urls = self.fetchWeb(searchParams, driver)
        websiteContents = await self.fetchMultipleUrls(urls)
        return websiteContents
    
    async def textExtractor(self, searchParams, driver):
        resultTexts = await self.resultExtract(searchParams, driver)
        text = [re.sub("[\s]{2,}", "", BeautifulSoup(result["result"], "html.parser").text.replace("\\n", "").replace("\\t", "").replace("\\r", "")) for result in resultTexts]
        sources = [result["source"] for result in resultTexts]
        
        return text, sources