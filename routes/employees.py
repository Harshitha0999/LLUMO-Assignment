from fastapi import APIRouter, HTTPException, status, Body
from typing import Optional, Dict, Any, List
from models import EmployeeCreate, EmployeeUpdate, EmployeeBase
from database import db
from pymongo.errors import DuplicateKeyError

router = APIRouter()

class Employee(EmployeeBase):
    employee_id: str

def _clean_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc
    doc.pop("_id", None)
    return doc

@router.post("/employees", status_code=status.HTTP_201_CREATED, response_model=Employee)
async def create_employee(emp: EmployeeCreate):
    exists = await db["employees"].find_one({"employee_id": emp.employee_id})
    if exists:
        raise HTTPException(status_code=400, detail="employee_id must be unique")
    data = emp.dict()
    await db["employees"].insert_one(data)
    return Employee(**data)

@router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    doc = await db["employees"].find_one({"employee_id": employee_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Employee not found")
    doc = _clean_doc(doc)
    return Employee(**doc)

@router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: str, upd: EmployeeUpdate = Body(...)):
    update_data = {k: v for k, v in upd.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Provide at least one field to update")
    result = await db["employees"].update_one({"employee_id": employee_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    doc = await db["employees"].find_one({"employee_id": employee_id})
    doc = _clean_doc(doc)
    return Employee(**doc)

@router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    res = await db["employees"].delete_one({"employee_id": employee_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"status": "deleted", "employee_id": employee_id}

@router.get("/employees", response_model=List[Employee])
async def list_employees(department: Optional[str] = None, limit: int = 100):
    query = {}
    if department:
        query["department"] = department
    cursor = db["employees"].find(query).sort("joining_date", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc = _clean_doc(doc)
        results.append(Employee(**doc))
    return results

@router.get("/employees/avg-salary")
async def avg_salary_by_department():
    pipeline = [
        {
            "$project": {
                "department": 1,
                "salary": {
                    "$cond": [
                        {"$isNumber": "$salary"},
                        "$salary",
                        {"$toDouble": "$salary"}
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": "$department",
                "avg_salary": {"$avg": "$salary"}
            }
        }
    ]
    cursor = db["employees"].aggregate(pipeline)
    out = []
    async for doc in cursor:
        out.append({"department": doc["_id"], "avg_salary": round(doc["avg_salary"], 2)})
    return out

@router.get("/employees/search", response_model=List[Employee])
async def search_by_skill(skill: str, limit: int = 3, skip: int = 0):
    cursor = db["employees"].find({"skills": skill}).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        doc = _clean_doc(doc)
        results.append(Employee(**doc))
    return results

# from fastapi import APIRouter, HTTPException, status
# from typing import Optional, Dict, Any
# from models import EmployeeCreate, EmployeeUpdate
# from database import db
# from pymongo.errors import DuplicateKeyError

# router = APIRouter()

# def _clean_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
#     if not doc:
#         return doc
#     doc.pop("_id", None)
#     return doc

# @router.post("/employees", status_code=status.HTTP_201_CREATED)
# async def create_employee(emp: EmployeeCreate):
#     data = emp.dict()
#     try:
#         await db["employees"].insert_one(data)
#     except DuplicateKeyError:
#         raise HTTPException(status_code=400, detail="employee_id must be unique")
#     return {"status": "created", "employee_id": emp.employee_id}

# @router.get("/employees/{employee_id}")
# async def get_employee(employee_id: str):
#     doc = await db["employees"].find_one({"employee_id": employee_id})
#     if not doc:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     return _clean_doc(doc)

# @router.put("/employees/{employee_id}")
# async def update_employee(employee_id: str, upd: EmployeeUpdate):
#     update_data = {k: v for k, v in upd.dict().items() if v is not None}
#     if not update_data:
#         raise HTTPException(status_code=400, detail="Provide at least one field to update")
#     result = await db["employees"].update_one({"employee_id": employee_id}, {"$set": update_data})
#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     doc = await db["employees"].find_one({"employee_id": employee_id})
#     return _clean_doc(doc)

# @router.delete("/employees/{employee_id}")
# async def delete_employee(employee_id: str):
#     res = await db["employees"].delete_one({"employee_id": employee_id})
#     if res.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     return {"status": "deleted", "employee_id": employee_id}

# @router.get("/employees")
# async def list_employees(department: Optional[str] = None, limit: int = 100):
#     query = {}
#     if department:
#         query["department"] = department
#     cursor = db["employees"].find(query).sort("joining_date", -1).limit(limit)
#     results = []
#     async for doc in cursor:
#         results.append(_clean_doc(doc))
#     if not results:
#         return {"message": "No employees found"}
#     return results

# @router.get("/employees/avg-salary")
# async def avg_salary_by_department():
#     pipeline = [
#         {
#             "$project": {
#                 "department": 1,
#                 "salary": {
#                     "$cond": [
#                         {"$isNumber": "$salary"},
#                         "$salary",
#                         {"$toDouble": "$salary"}
#                     ]
#                 }
#             }
#         },
#         {
#             "$group": {
#                 "_id": "$department",
#                 "avg_salary": {"$avg": "$salary"}
#             }
#         }
#     ]
#     cursor = db["employees"].aggregate(pipeline)
#     out = []
#     async for doc in cursor:
#         out.append({"department": doc["_id"], "avg_salary": round(doc["avg_salary"], 2)})
#     if not out:
#         return {"message": "No data to calculate average salary"}
#     return out

# @router.get("/employees/search")
# async def search_by_skill(skill: str):
#     cursor = db["employees"].find({
#         "skills": {"$elemMatch": {"$eq": skill}}
#     })
#     results = []
#     async for doc in cursor:
#         results.append(_clean_doc(doc))
#     if not results:
#         return {"message": f"No employees found with skill '{skill}'"}
#     return results

# @router.get("/employees/search")
# async def search_by_skill(skill: str):
#     cursor = db["employees"].find({"skills": skill})
#     results = []
#     async for doc in cursor:
#         results.append(_clean_doc(doc))
#     if not results:
#         return {"message": f"No employees found with skill '{skill}'"}
#     return results

# from fastapi import APIRouter, HTTPException, status
# from typing import List, Optional, Dict, Any
# from models import EmployeeCreate, EmployeeUpdate
# from database import db
# from pymongo.errors import DuplicateKeyError

# router = APIRouter()

# # Helper to remove MongoDB _id
# def _clean_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
#     if not doc:
#         return doc
#     doc.pop("_id", None)
#     return doc

# # Create Employee
# @router.post("/employees", status_code=status.HTTP_201_CREATED)
# async def create_employee(emp: EmployeeCreate):
#     data = emp.dict()
#     try:
#         await db["employees"].insert_one(data)
#     except DuplicateKeyError:
#         raise HTTPException(status_code=400, detail="employee_id must be unique")
#     return {"status": "created", "employee_id": emp.employee_id}

# # Get Employee by ID
# @router.get("/employees/{employee_id}")
# async def get_employee(employee_id: str):
#     doc = await db["employees"].find_one({"employee_id": employee_id})
#     if not doc:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     return _clean_doc(doc)

# # Update Employee
# @router.put("/employees/{employee_id}")
# async def update_employee(employee_id: str, upd: EmployeeUpdate):
#     update_data = {k: v for k, v in upd.dict().items() if v is not None}
#     if not update_data:
#         raise HTTPException(status_code=400, detail="Provide at least one field to update")
#     result = await db["employees"].update_one({"employee_id": employee_id}, {"$set": update_data})
#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     doc = await db["employees"].find_one({"employee_id": employee_id})
#     return _clean_doc(doc)

# # Delete Employee
# @router.delete("/employees/{employee_id}")
# async def delete_employee(employee_id: str):
#     res = await db["employees"].delete_one({"employee_id": employee_id})
#     if res.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     return {"status": "deleted", "employee_id": employee_id}

# # List Employees by Department
# @router.get("/employees")
# async def list_employees(department: Optional[str] = None, limit: Optional[int] = 100):
#     q = {}
#     if department:
#         q["department"] = department
#     cursor = db["employees"].find(q).sort("joining_date", -1).limit(limit)
#     results = []
#     async for doc in cursor:
#         results.append(_clean_doc(doc))
#     return results

# # Average Salary by Department
# @router.get("/employees/avg-salary")
# async def avg_salary_by_department():
#     pipeline = [
#         {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}}
#     ]
#     cursor = db["employees"].aggregate(pipeline)
#     out = []
#     async for doc in cursor:
#         out.append({"department": doc["_id"], "avg_salary": round(doc["avg_salary"])})
#     return out

# # Search Employees by Skill
# @router.get("/employees/search")
# async def search_by_skill(skill: str):
#     cursor = db["employees"].find({"skills": skill})
#     results = []
#     async for doc in cursor:
#         results.append(_clean_doc(doc))
#     return results
