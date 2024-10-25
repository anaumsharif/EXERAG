import sqlite3


def create_connection(db_name):
    """
    Create a database connection to a SQLite database.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        print(f"Connected to {db_name} successfully.")
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn):
    """
    Create a table in the SQLite database.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS legal_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_name TEXT NOT NULL,
            type_of_document TEXT NOT NULL
        )
        """
        )
        conn.commit()
        print("Table created successfully.")
    except sqlite3.Error as e:
        print(e)


def insert_multiple_documents(conn, documents):
    """
    Insert multiple documents into the documents table.
    """
    try:
        cursor = conn.cursor()
        cursor.executemany(
            """
        INSERT INTO legal_docs (document_name, type_of_document)
        VALUES (?, ?)
        """,
            documents,
        )
        conn.commit()
        print("Multiple documents inserted successfully.")
    except sqlite3.Error as e:
        print(e)


def close_connection(conn):
    """
    Close the database connection.
    """
    try:
        conn.close()
        print("Connection closed successfully.")
    except sqlite3.Error as e:
        print(e)


# if __name__ == "__main__":
#     # Step 1: Create a connection to the database
#     conn = create_connection('documents.db')

#     # Step 2: Create the documents table
#     if conn is not None:
#         create_table(conn)

#         # Step 3: Insert 10 documents
#         documents = [
#             ('NDA - Botree Software', 'NDA'),
#             ('NDA - Diligent Global Tech (05.09.2023)', 'NDA'),
#             ('Nvtq_Prop_GCPL_ANV_5th_May_ 2024', 'Proposal'),
#             ('SLI_Pro_GAVL_Anniversary_5th_MAY_ 2023.V3', 'Proposal'),
#             ('SLI_Pro_GCPL_INDIA_Anniversary_05th_MAY_ 2023.V3', 'Proposal'),
#             ('SLI_Pro_GIL_CHEMICAL_Anniversary_05th_May_ 2023.V3', 'Proposal'),
#             ('TCS ADDENDUM 5 TO AMEND TERMS AND SCOPE  OF THE GCPL AGREEMENT effective 1st Dec 2020', 'Addendum'),
#             ('TCS ADDENDUM NO 11 GCPL AGREEMENT Helpdesk dated 22032024 Final', 'Addendum'),
#             ('Accenture -1 FTE support Apr 18 -Mar 19', 'Addendum'),
#             ('botree proposal', 'Proposal'),
#             ('CYQUREX SYSTEMS MSA & SOW', 'Aggrement'),
#             ('Exponentia NDA-GCPL', 'NDA'),
#             ('LOVEINSTORE TECHNOLOGIES PRIVATE LIMITED-NDA', 'NDA'),
#             ('Microsoft  Premier Support -FY 20-21', 'Aggrement'),
#             ('PCR_Rate Card_2023_V1.1a', 'PCR'),
#             ('PCR_Resource Optimization_Apr 2024_V1.1', 'PCR'),
#             ('Proposal_ Qlik Resources Deployment_GCPL_Exponentia.ai_1st Apr-24_31st Mar-25 Ver 1.0_07.06.2024',
#              'Proposal'),
#         ]
#         insert_multiple_documents(conn, documents)

#         # Step 4: Close the connection
#         close_connection(conn)
#     else:
#         print("Error! Cannot create the database connection.")
