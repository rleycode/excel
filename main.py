from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from excel_parser import parse_excel_file
from price_parser import parse_excel_rows
from business_logic import apply_business_rules

app = FastAPI(title="Excel Parser API", description="API для парсинга прайс-листов Excel")

@app.post("/parse-excel/")
async def parse_excel(file: UploadFile = File(...)):
    """
    Эндпоинт для загрузки и парсинга Excel файла
    """
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Формат файла должен быть .xlsx или .xls")
    
    try:
        content = await file.read()
        raw_data = parse_excel_file(content)  # просто листы → строки
        normalized = parse_excel_rows(raw_data)  # разбор цен/названий
        enriched = apply_business_rules(normalized)  # категории, наценки
        
        return JSONResponse(content=jsonable_encoder({
            "filename": file.filename,
            "products_count": len(enriched),
            "products": enriched
        }))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Excel Parser API готов к работе", "endpoints": ["POST /parse-excel/"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
