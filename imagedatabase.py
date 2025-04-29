def store_analysis_result(self, image_path, prompt, result):
    try:
        cursor = conn.cursor()
        
        # SQL to insert analysis result
        insert_query = """
        INSERT INTO image_analyses 
        (image_path, prompt, analysis_result, analysis_date) 
        VALUES (%s, %s, %s, NOW())
        """
        
        # Execute the query
        cursor.execute(insert_query, (image_path, prompt, result))
        
        # Commit the transaction
        conn.commit()
        
        print("Analysis result stored successfully")
    
    except mysql.connector.Error as err:
        print(f"Error storing analysis result: {err}")
    finally:
        if cursor:
            cursor.close()