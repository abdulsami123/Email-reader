import os
import google.generativeai as genai
import reader
import util
import crud 




#This loads the Gemini-API key
genai.configure(api_key=os.environ.get("GEMINI_API"))

#This selects the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

#Here we use the reader file to extract the links and their timestamps in the emails
text = reader.main()['links']
timestamps = reader.main()['timestamp']

#Here we are dumping the emails in the 'Emails' table
crud.update_Emails(text,timestamps)

#Here we are querying the links from the database
links = crud.select_links()

#Here we are extracting the text from the links in the Db & performing summarization inference
for x in links[0:10]:
    text = util.extract_text(x)  # Get text first
    if not text:  # Skip if text is None or empty
        continue
    
    title = util.extract_title(x)  # Only fetch title if text is valid
    response = model.generate_content(f"Summarize: {text}")
    crud.update_Summary(response.text, x, title)
        

    



