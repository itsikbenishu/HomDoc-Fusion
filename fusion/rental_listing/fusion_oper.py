from sqlmodel import Session
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from entities.home_doc.service import HomeDocService
from entities.home_doc.repository import HomeDocRepository
from entities.common.enums import HomeDocCategoriesEnum, HomeDocTypeEnum
from entities.home_doc.models import HomeDocs
from pipeline.operation import Operation
from db.session import engine

class FusionOper(Operation):
    def __init__(self):
        super().__init__()

    def run(self, input):
        residence_repo = ResidenceRepository.get_instance()
        residence_srv = ResidenceService.get_instance(residence_repo)
        home_doc_repo = HomeDocRepository.get_instance()
        home_doc_srv = HomeDocService.get_instance(home_doc_repo)

        with Session(engine) as session:
            # ============================================
            # דוגמות ל-HomeDocService
            # ============================================
            
            # 1. יצירת HomeDoc חדש (דירה עצמאית)
            home_doc_data = {
                "interior_entity_key": "רחוב הרצל 11, רמת גן, ישראל",
                "category": HomeDocCategoriesEnum.RESIDENTIAL_BUILDING,
                "type": HomeDocTypeEnum.PROPERTY,
                "description": "דירת 3 חדרים עם מרפסת",
                "extra_data": [
                    {"characteristic": "floor", "value": "3"},
                    {"characteristic": "elevator", "value": "true"},
                    {"characteristic": "parking", "value": "1"}
                ]
            }
            
            try:
                # יצירת HomeDoc
                new_home_doc = home_doc_srv.create(home_doc_data, session)
                print(f"נוצר HomeDoc חדש עם ID: {new_home_doc.id}")
                
                # 2. קבלת HomeDoc לפי ID
                retrieved_home_doc = home_doc_srv.get_by_id(new_home_doc.id, session)
                print(f"נמצא HomeDoc: {retrieved_home_doc.interior_entity_key}")
                
                # 3. עדכון HomeDoc
                update_data = {
                    "description": "דירת 3 חדרים עם מרפסת ומחסן",
                    "extra_data": [
                        {"characteristic": "floor", "value": "3"},
                        {"characteristic": "elevator", "value": "true"},
                        {"characteristic": "parking", "value": "1"},
                        {"characteristic": "storage", "value": "true"}
                    ]
                }
                
                updated_home_doc = home_doc_srv.update(new_home_doc.id, update_data, session)
                print(f"עודכן HomeDoc: {updated_home_doc.description}")
                
                # 4. חיפוש HomeDocs עם פילטרים מתקדמים
                query_params = {
                    # פילטרים בסיסיים
                    "category": HomeDocCategoriesEnum.RESIDENTIAL_BUILDING.value,
                    "type": HomeDocTypeEnum.PROPERTY.value,
                    
                    # פילטרי טווח
                    "id[$gte]": 1,  # ID גדול או שווה ל-1
                    "id[$lte]": 1000,  # ID קטן או שווה ל-1000
                    
                    # פילטר LIKE עם wildcards
                    "description[$ILIKE]": "חדרים",  # מכיל את המילה "חדרים"
                    "description[$wildcard]": "both",  # wildcards משני הצדדים
                    
                    # פילטר על external_id
                    "external_id[$LIKE]": "EXT%",  # מתחיל ב-EXT
                    "external_id[$wildcard]": "end",  # wildcard בסוף
                    
                    # פילטרי תאריך
                    "created_at[$gte]": "2024-01-01",
                    "created_at[$date]": "true",  # מציין שזה פילטר תאריך
                    
                    # פילטר IN
                    "interior_entity_key[$in]": "רחוב הרצל 11, רמת גן, ישראל,DOC_APT_002_MAIN,DOC_APT_003_MAIN",
                    
                    # פרמטרי עימוד ומיון
                    "page": 1,
                    "limit": 10,
                    "sort": "-created_at,id",  # מיון לפי תאריך יצירה (יורד) ואז ID (עולה)
                    "tz": "Asia/Jerusalem"  # אזור זמן
                }
                
                home_docs_list = home_doc_srv.get(session, query_params)
                print(f"נמצאו {len(home_docs_list)} דירות")
                
                # 5. מחיקת HomeDoc
                # home_doc_srv.delete(new_home_doc.id, session)
                # print(f"נמחק HomeDoc עם ID: {new_home_doc.id}")
                
            except ValueError as ve:
                print(f"שגיאת ולידציה: {ve}")
            except Exception as e:
                print(f"שגיאה ב-HomeDocService: {e}")
            
            # ============================================
            # דוגמות נוספות ל-HomeDocRepository
            # ============================================
            
            try:
                # קבלת IDs לפי External IDs
                external_ids = ["EXT123456", "EXT789012", "EXT345678"]
                ids_mapping = home_doc_repo.get_ids_by_external_ids(external_ids, session)
                print(f"מיפוי External IDs ל-IDs: {ids_mapping}")
                
            except Exception as e:
                print(f"שגיאה ב-HomeDocRepository: {e}")
            
            # ============================================
            # דוגמות ל-ResidenceRepository
            # ============================================
            
            try:
                # 1. יצירת Residence מלא (עם specs ו-dimensions) - בית עצמאי
                residence_data = {
                    # נתוני HomeDocs
                    "interior_entity_key": "5448 N 35th St, Milwaukee, WI 57223, USA",
                    "category": HomeDocCategoriesEnum.RESIDENTIAL_BUILDING,
                    "type": HomeDocTypeEnum.PROPERTY,
                    "description": "בית פרטי 4 חדרים עם גינה",
                    "extra_data": [
                        {"characteristic": "garden", "value": "true"},
                        {"characteristic": "garage", "value": "3 ars"},
                        {"characteristic": "pool", "value": "false"}
                    ],
                    
                    # נתוני ResidenceSpecsAttributes
                    "area": 120.5,
                    "sub_entities_quantity": 4,
                    "construction_year": 2020,
                    
                    # נתוני HomeDocsDimensions
                    "length": 15,
                    "width": 10
                }
                
                # יצירת Residence
                new_residence = residence_srv.create(residence_data, session)
                print(f"נוצר Residence חדש עם ID: {new_residence.id}")
                
                # 2. קבלת Residence לפי ID (עם כל הנתונים המורחבים)
                retrieved_residence = residence_srv.get_by_id(new_residence.id, session)
                print(f"נמצא Residence: {retrieved_residence.interior_entity_key}")
                print(f"שטח: {getattr(retrieved_residence, 'specs', None)}")
                print(f"מידות: {getattr(retrieved_residence, 'dimensions', None)}")
                
                # 3. עדכון Residence מלא
                residence_update_data = {
                    # עדכון HomeDocs
                    "description": "בית פרטי 4 חדרים עם גינה ובריכה",
                    "extra_data": [
                        {"characteristic": "garden", "value": "true"},
                        {"characteristic": "garage", "value": "2 cars"},
                        {"characteristic": "pool", "value": "true"},
                        {"characteristic": "solar panels", "value": "true"}
                    ],
                    
                    # עדכון ResidenceSpecsAttributes
                    "area": 125.0,
                    "sub_entities_quantity": 5,
                    
                    # עדכון HomeDocsDimensions
                    "length": 16,
                    "width": 11
                }
                
                updated_residence = residence_srv.update(new_residence.id, residence_update_data, session)
                print(f"עודכן Residence: {updated_residence.description}")
                
                # 4. חיפוש Residences עם פילטרים מתקדמים מרובי טבלאות
                residence_query_params = {
                    # פילטרים על HomeDocs (הטבלה הראשית)
                    "category": HomeDocCategoriesEnum.RESIDENTIAL_BUILDING.value,
                    "type": HomeDocTypeEnum.PROPERTY.value,
                    "description[$ILIKE]": "חצר",
                    "description[$wildcard]": "both",
                    
                    # פילטרי תאריך על HomeDocs
                    "created_at[$gte]": "2023-01-01",
                    "created_at[$lte]": "2024-12-31", 
                    "created_at[$date]": "true",
                    
                    # פילטרי external_id
                    
                    "construction_year[$gte]": 2015,  # נבנה אחרי 2015
                    "construction_year[$lte]": 2025,  # נבנה לפני 2025
                    "sub_entities_quantity[$gte]": 3,  # לפחות 3 חדרים
                    "sub_entities_quantity[$in]": "3,4,6",  # 3, 4 או 5 חדרים
                    
                                        
                    # פרמטרי עימוד ומיון
                    "page": 1,
                    "limit": 20,
                    "sort": "-area,construction_year,-created_at",  # מיון לפי שטח (יורד), שנת בנייה (עולה), תאריך יצירה (יורד)
                    "tz": "Asia/Jerusalem"
                }
                
                residences_list = residence_srv.get(session, residence_query_params)
                print(f"נמצאו {len(residences_list)} בתים העונים לקריטריונים")
                # הצגת פרטים על הבתים שנמצאו
                for residence in residences_list[:3]:  # הצגת 3 הראשונים
                    specs = getattr(residence, 'specs', None)
                    dimensions = getattr(residence, 'dimensions', None)
                    print(f"  - {residence.interior_entity_key}: "
                          f"שטח {specs.area if specs else 'לא ידוע'} מ\"ר, "
                          f"מידות {dimensions.length if dimensions else '?'}x{dimensions.width if dimensions else '?'}")
                
            except Exception as e:
                print(f"שגיאה ב-ResidenceRepository: {e}")
            
            # ============================================
            # דוגמות ליצירת ישויות נפרדות בלי היררכיה
            # ============================================
            
            try:
                # יצירת דירות עצמאיות בלי בניין אב
                apartments_data = [
                    {
                        "interior_entity_key": "רחוב הרצל 5, רמת גן, ישראל",
                        "category": HomeDocCategoriesEnum.RESIDENTIAL_BUILDING,
                        "type": HomeDocTypeEnum.PROPERTY,
                        "extra_data": [
                        ]
                    },
                    {
                        "external_id": "APT_INDEP_002",
                        "interior_entity_key": "רחוב הרצל 9, רמת גן, ישראל",
                        "category": HomeDocCategoriesEnum.RESIDENTIAL_BUILDING,
                        "type": HomeDocTypeEnum.PROPERTY,
                        "extra_data": [
                            {"characteristic": "penthouse", "value": "true"}
                        ]
                    },
                    {
                        "interior_entity_key": "רחוב הרצל 11, באר שבע, ישראל",
                        "category": HomeDocCategoriesEnum.RESIDENTIAL_BUILDING,
                        "type": HomeDocTypeEnum.PROPERTY,
                        "extra_data": [
                            {"characteristic": "ground_floor", "value": "true"}
                        ]
                    }
                ]
                
                # יצירת דירות עצמאיות
                created_apartments = []
                for apt_data in apartments_data:
                    apartment = home_doc_srv.create(apt_data, session)
                    created_apartments.append(apartment)
                    print(f"נוצרה דירה עצמאית: {apartment.interior_entity_key}")
                
                # יצירת בתים עצמאיים
                houses_data = [
                    {
                        "interior_entity_key": "1ט39 SW 1st Ave, Portland, OR 93201, USA",
                        "category": HomeDocCategoriesEnum.RESIDENTIAL_BUILDING,
                        "type": HomeDocTypeEnum.PROPERTY,
                        "extra_data": [
                        ],
                        "area": 200.0,
                        "sub_entities_quantity": 6,
                        "construction_year": 2018,
                        "length": 20,
                        "width": 15
                    },
                    {
                        "external_id": "HOUSE_INDEP_002", 
                        "interior_entity_key": "1537 SW 1st Ave, Portland, OR 95201, USA",
                        "category": HomeDocCategoriesEnum.RESIDENTIAL_BUILDING,
                        "type": HomeDocTypeEnum.PROPERTY,
                        "extra_data": [
                            {"characteristic": "private_yard", "value": "true"},
                            {"characteristic": "parking_spots", "value": "2"}
                        ],
                        "area": 150.0,
                        "sub_entities_quantity": 4,
                        "construction_year": 2021,
                        "length": 18,
                        "width": 12
                    }
                ]
                
                # יצירת בתים עצמאיים
                created_houses = []
                for house_data in houses_data:
                    house = home_doc_srv.create(house_data, session)
                    created_houses.append(house)
                    print(f"נוצר בית עצמאי: {house.interior_entity_key}")
                
            except Exception as e:
                print(f"שגיאה ביצירת ישויות עצמאיות: {e}")
