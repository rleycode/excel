import pandas as pd
import io
from typing import Dict, Any
from fastapi import HTTPException

def parse_excel_file(file_content: bytes) -> Dict[str, Any]:
    """
    Парсинг Excel файла с множественными листами
    """
    try:
        # Читаем все листы Excel файла
        xls = pd.ExcelFile(io.BytesIO(file_content))
        result = {}
        
        for sheet_name in xls.sheet_names:
            # Читаем лист как есть, без предположений о структуре
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            
            # Преобразуем в список словарей для удобства
            sheet_data = []
            for _, row in df.iterrows():
                # Фильтруем NaN значения и конвертируем datetime в строки
                clean_row = []
                for cell in row:
                    if pd.isna(cell):
                        clean_row.append("")
                    elif isinstance(cell, (pd.Timestamp, pd.Timedelta)):
                        clean_row.append(str(cell))
                    else:
                        clean_row.append(cell)
                sheet_data.append(clean_row)
            
            result[sheet_name] = sheet_data
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при парсинге Excel: {str(e)}")