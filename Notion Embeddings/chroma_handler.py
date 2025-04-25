from Chroma import ChromaHandler
from chromadb.utils import embedding_functions

chroma_handler = ChromaHandler(collection_name='test_collection')

student_info = """
Alexandra Thompson, a 19-year-old computer science sophomore with a 3.7 GPA,
is a member of the programming and chess clubs who enjoys pizza, swimming, and hiking
in her free time in hopes of working at a tech company after graduating from the University of Washington.
"""

club_info = """
The university chess club provides an outlet for students to come together and enjoy playing
the classic strategy game of chess. Members of all skill levels are welcome, from beginners learning
the rules to experienced tournament players. The club typically meets a few times per week to play casual games,
participate in tournaments, analyze famous chess matches, and improve members' skills.
"""

university_info = """
The University of Washington, founded in 1861 in Seattle, is a public research university
with over 45,000 students across three campuses in Seattle, Tacoma, and Bothell.
As the flagship institution of the six public universities in Washington state,
UW encompasses over 500 buildings and 20 million square feet of space,
including one of the largest library systems in the world.
"""

documents = [student_info, club_info, university_info]

chroma_handler.add_document(documents, ['id1', 'id2', 'id3'])
response_embedding = chroma_handler.query_document_embedding(chroma_handler.embedding_function(["What is the student's name?"]), number = 1)


response_text = chroma_handler.query_text_document("What is the student's name?", number = 5)


print(response_embedding)
print(response_text)
