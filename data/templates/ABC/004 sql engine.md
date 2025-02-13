Для подключения к БД воспользуемся библиотеками pandas и sqlalchemy
```python
import os
import pandas as pd
from sqlalchemy import create_engine, text


# SUPABASE = "..." - supabase connection string

supabase_connection_string = os.getenv('SUPABASE')
if not supabase_connection_string:
	raise ValueError("SUPABASE environment variable is not set")

engine = create_engine(supabase_connection_string)

def select(sql: str) -> pd.DataFrame:
    """Выполняет SQL-запрос и возвращает результат в виде DataFrame.
    Args:
        sql (str): SQL-запрос
    Returns:
        pd.DataFrame: Результат запроса
    """

    sql = text(sql)
	
    return pd.read_sql(sql, engine)
```