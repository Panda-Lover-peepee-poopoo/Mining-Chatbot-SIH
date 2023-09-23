import sqlite3
import spacy

# Initialize the chatbot
print("Welcome to the Mining Industry Chatbot. You can ask questions about mining Acts, Rules, Regulations, Guidelines, Methodology, or Corrigenda. Type 'exit' to quit.")

# Load spaCy model for better natural language understanding
nlp = spacy.load("en_core_web_sm")

# Connect to the SQLite database
conn = sqlite3.connect('mining_data.db')
cursor = conn.cursor()

# Define data categories
categories = ['Acts', 'Rules', 'Regulations', 'Guidelines', 'Methodology', 'Corrigenda']

# Sample data insertion for each category
sample_data = {
      'Acts': [
            ('Mining Act',
             'The Mining Act governs mining operations in India. It covers various aspects of mining, including '
             'exploration, licensing, and environmental regulations. The Act is designed to ensure the sustainable '
             'and responsible extraction of minerals while safeguarding the environment and the rights of local '
             'communities.'),
            ('Mineral Conservation and Development Rules',
             'These rules outline procedures for mineral conservation. They emphasize the efficient use of mineral '
             'resources, the prevention of illegal mining, and the promotion of scientific mining practices. The '
             'rules set forth guidelines for mining leaseholders to follow in managing mineral reserves and ensuring '
             'their sustainable development.'),
      ],
      'Rules': [
            ('Mining Safety Rules',
             'Safety rules for mining operations are crucial to protect the health and well-being of mining '
             'personnel. These rules establish safety standards and protocols for various aspects of mining, '
             'including underground and surface operations, explosives handling, and ventilation. Compliance with '
             'these rules is essential to minimize accidents and ensure a safe working environment for miners.'),
            ('Environmental Protection Rules',
             'Rules for environmental protection in mining are aimed at minimizing the ecological impact of mining '
             'activities. They prescribe measures for environmental impact assessments, pollution control, '
             'and reclamation of mined areas. Adhering to these rules is vital to mitigate the environmental '
             'footprint of mining operations and fulfill legal obligations.'),
      ],
      'Regulations': [
            ('Mining Regulations',
             'Regulations related to mining activities provide detailed guidance on compliance with the Mining Act '
             'and Rules. These regulations cover a wide range of topics, including lease applications, royalties, '
             'and safety inspections. They are essential for ensuring that mining companies and operators meet legal '
             'and operational requirements in their mining activities.'),
            ('Export and Import Regulations',
             'Rules for exporting and importing minerals govern the international trade of mined products. These '
             'regulations specify documentation and licensing requirements for the export and import of minerals. '
             'Compliance with these rules is necessary to facilitate international trade while preventing illegal '
             'mineral exports and imports.'),
      ],
      'Guidelines': [
            ('Mining Guidelines',
             'Guidelines for sustainable mining practices offer recommendations for responsible mining operations. '
             'They advocate for environmentally conscious practices, community engagement, and ethical conduct. '
             'Following these guidelines is not only a legal requirement but also contributes to the industry\'s '
             'social and environmental responsibility.'),
            ('Safety Guidelines',
             'Safety guidelines for mining personnel provide practical advice for ensuring the well-being of miners. '
             'They cover topics such as personal protective equipment (PPE), emergency response, and first aid '
             'procedures. Implementing these guidelines is essential to prevent accidents and safeguard the health of '
             'workers.'),
      ],
      'Methodology': [
            ('Mining Methodology',
             'The methodology for extracting minerals from mines outlines the step-by-step process of mining '
             'operations. It encompasses exploration, drilling, blasting, ore extraction, and processing. A '
             'well-defined methodology is essential to optimize resource recovery while minimizing environmental '
             'impacts and ensuring worker safety.'),
            ('Environmental Assessment Methodology',
             'Methodology for environmental impact assessment in mining is crucial for evaluating the potential '
             'ecological consequences of mining projects. It involves comprehensive studies to assess air and water '
             'quality, wildlife habitats, and socio-economic factors. Following this methodology helps mining '
             'companies make informed decisions and mitigate environmental risks.'),
      ],
      'Corrigenda': [
            ('Mining Corrigendum',
             'This corrigendum corrects errors in previous mining regulations. It may include updates to legislative '
             'texts, clarifications, or corrections of typographical errors. Staying informed about corrigenda is '
             'essential for legal compliance and ensuring that mining operations adhere to the latest regulatory '
             'requirements.'),
            ('Safety Corrigendum',
             'Corrigendum related to safety regulations in mining addresses safety-related updates or changes in '
             'safety guidelines. Staying up to date with safety corrigenda is critical for maintaining a safe working '
             'environment and complying with the latest safety standards.'),
      ]
}

for category, data in sample_data.items():
      for title, content in data:
            cursor.execute(f"INSERT INTO {category} (title, content) VALUES (?, ?)", (title, content))
            conn.commit()


# Function for keyword extraction from user query
def extract_keywords(query):
      keywords = []
      doc = nlp(query)
      for token in doc:
            if token.pos_ in ["NOUN", "ADJ"]:
                  keywords.append(token.text)
      return keywords


# Function for searching and retrieving data
def search_data(query, category=None):
      keywords = extract_keywords(query)
      matched_results = []

      if category:
            # If a specific category is specified, search only in that category
            query_str = f"SELECT title, content FROM {category} WHERE content LIKE ?"
            for keyword in keywords:
                  cursor.execute(query_str, ('%' + keyword + '%',))
                  results = cursor.fetchall()
                  matched_results.extend([(category, result[0], result[1]) for result in results])
      else:
            # Search in all categories if no specific category is provided
            for cat in categories:
                  query_str = f"SELECT title, content FROM {cat} WHERE content LIKE ?"
                  for keyword in keywords:
                        cursor.execute(query_str, ('%' + keyword + '%',))
                        results = cursor.fetchall()
                        matched_results.extend([(cat, result[0], result[1]) for result in results])

      return matched_results


# Sample interaction with the chatbot
while True:
      user_query = input("You: ").strip().lower()

      if user_query == 'exit':
            break

      # Handle greetings and farewells
      if user_query in ['hi', 'hello', 'hey']:
            print("Chatbot: Hello! How can I assist you today?")
            continue
      elif user_query in ['bye', 'goodbye']:
            print("Chatbot: Goodbye! If you have more questions in the future, feel free to return.")
            break

      # Check if the user query contains a category name
      for cat in categories:
            if cat.lower() in user_query:
                  # Search in the specified category
                  matched_results = search_data(user_query, category=cat)
                  break
      else:
            # If no category is specified in the query, search in all categories
            matched_results = search_data(user_query)

      if matched_results:
            # Group results by category and prioritize Acts and Rules
            result_dict = {}
            for category, title, content in matched_results:
                  if category not in result_dict:
                        result_dict[category] = set()  # Use a set to prevent duplicate entries
                  result_dict[category].add((title, content))

            # Display the most relevant information
            for category, results in result_dict.items():
                  print(f"Relevant {category}:")
                  for title, content in results:
                        print(f"Title: {title}\nContent: {content}\n")
      else:
            print("Chatbot: I couldn't find any relevant information. Would you like me to search in other categories for relevant information? (Yes/No)")
            user_choice = input("You: ").strip().lower()
            if user_choice == 'yes':
                  # If the user wants to search in other categories, perform a broader search
                  matched_results = search_data(user_query)
                  if matched_results:
                        # Display the most relevant information from all categories
                        result_dict = {}
                        for category, title, content in matched_results:
                              if category not in result_dict:
                                    result_dict[category] = set()  # Use a set to prevent duplicate entries
                              result_dict[category].add((title, content))

                        # Display the most relevant information
                        for category, results in result_dict.items():
                              print(f"Relevant {category}:")
                              for title, content in results:
                                    print(f"Title: {title}\nContent: {content}\n")
                  else:
                        print("Chatbot: I couldn't find any relevant information in other categories.")
            else:
                  print("Chatbot: If you have more specific queries or need assistance, feel free to ask.")

# Close the database connection
conn.close()
