import json
import os
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Event, Performance, Team, ScoresArtFaf, ScoresTechFaf, ScoresArtNaf, ScoresTechNaf, Judge

router = APIRouter()
templates = Jinja2Templates(directory="templates")

JUDGES_FILE = "judges.json"

def load_judges() -> List[Dict[str, Any]]:
    """Загрузить судей из JSON файла"""
    if os.path.exists(JUDGES_FILE):
        with open(JUDGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_judges(judges: List[Dict[str, Any]]):
    """Сохранить судей в JSON файл"""
    with open(JUDGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(judges, f, ensure_ascii=False, indent=2)

def verify_admin_password(password: str) -> bool:
    """Проверить пароль администратора"""
    return password == "mustiness"

def find_judge_by_password(password: str) -> Dict[str, Any] | None:
    """Найти судью по паролю"""
    judges = load_judges()
    for judge in judges:
        if judge.get("password_hash") == password:
            return judge
    return None

def get_judge_role_and_system(role: str) -> tuple[str, str]:
    """Разделить роль на тип и систему (faf/naf)"""
    if "_faf" in role:
        return role.replace("_faf", ""), "faf"
    elif "_naf" in role:
        return role.replace("_naf", ""), "naf"
    else:
        return role, "faf"  # по умолчанию FAF для старых ролей

# Mock data for dashboard (пока что тестовые данные)
def get_naf_results():
    return [
        {"name": "Танец с саблями", "team": "Театр фехтования", "score": 1.85},
        {"name": "Битва титанов", "team": "Школа боевых искусств", "score": 1.92},
        {"name": "Легенда о рыцаре", "team": "Клуб исторического фехтования", "score": 1.78}
    ]

def get_faf_results():
    return [
        {"name": "Танец с саблями", "team": "Театр фехтования", "score": 8.5},
        {"name": "Битва титанов", "team": "Школа боевых искусств", "score": 9.2},
        {"name": "Легенда о рыцаре", "team": "Клуб исторического фехтования", "score": 7.8}
    ]

@router.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    """Главная страница - единая форма входа"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, password: str = Form(...)):
    """Обработка входа"""
    if verify_admin_password(password):
        # Админ
        response = RedirectResponse(url="/admin/manage", status_code=303)
        response.set_cookie(key="admin_auth", value="true", httponly=True)
        return response
    else:
        # Проверить, является ли пароль судьи
        judge = find_judge_by_password(password)
        if judge:
            # Судья - перенаправить на форму соответствующей специализации
            role_type, system = get_judge_role_and_system(judge["role"])
            response = RedirectResponse(url=f"/judge/{role_type}/{system}", status_code=303)
            response.set_cookie(key="judge_auth", value=str(judge["id"]), httponly=True)
            return response
        else:
            # Неверный пароль
            return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный пароль"})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Дашборд с результатами"""
    naf_results = get_naf_results()
    faf_results = get_faf_results()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "naf_results": naf_results,
        "faf_results": faf_results
    })

@router.get("/admin/manage", response_class=HTMLResponse)
async def admin_manage_page(request: Request):
    """Страница управления судьями"""
    # Проверить куку аутентификации
    if request.cookies.get("admin_auth") != "true":
        return RedirectResponse(url="/", status_code=303)

    judges = load_judges()
    return templates.TemplateResponse("admin.html", {"request": request, "judges": judges})

@router.post("/admin/add_judge")
async def add_judge(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    password: str = Form(...)
):
    """Добавить нового судью"""
    # Проверить куку аутентификации
    if request.cookies.get("admin_auth") != "true":
        raise HTTPException(status_code=403, detail="Не авторизован")

    judges = load_judges()

    # Проверить, существует ли уже такой email
    if any(j["email"] == email for j in judges):
        judges = load_judges()
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "judges": judges,
            "error": "Судья с таким email уже существует"
        })

    # Создать нового судью
    new_judge = {
        "id": len(judges) + 1,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "role": role,
        "password_hash": password,  # В реальности нужно хешировать, но по запросу сохраняем как есть
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }

    judges.append(new_judge)
    save_judges(judges)

    # Перенаправить обратно на страницу управления
    return RedirectResponse(url="/admin/manage", status_code=303)

@router.post("/admin/logout")
async def admin_logout():
    """Выход из админ-панели"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="admin_auth")
    return response

# Роуты для форм судей разных специализаций
@router.get("/judge/{role_type}/{system}", response_class=HTMLResponse)
async def judge_dashboard(request: Request, role_type: str, system: str, db: Session = Depends(get_db)):
    """Дашборд судьи с выбором номеров"""
    # Проверить аутентификацию судьи
    judge_id = request.cookies.get("judge_auth")
    if not judge_id:
        return RedirectResponse(url="/", status_code=303)

    judges = load_judges()
    judge = next((j for j in judges if str(j["id"]) == judge_id), None)
    expected_role = f"{role_type}_{system}"
    if not judge or judge["role"] != expected_role:
        return RedirectResponse(url="/", status_code=303)

    # Получить мероприятие "тест"
    test_event = db.query(Event).filter(Event.name_event == "тест").first()
    if not test_event:
        # Если мероприятие не найдено, используем mock данные
        disciplines = {
            "Соло": [
                {"id": 1, "name": "Танец со шпагой", "team": "Театр фехтования"},
                {"id": 2, "name": "Соло на рапире", "team": "Школа боевых искусств"}
            ],
            "Дуэль": [
                {"id": 3, "name": "Дуэль на шпагах", "team": "Клуб исторического фехтования"},
                {"id": 4, "name": "Поединок саблями", "team": "Театр фехтования"}
            ],
            "Группа": [
                {"id": 5, "name": "Групповой танец", "team": "Школа боевых искусств"},
                {"id": 6, "name": "Командная битва", "team": "Клуб исторического фехтования"}
            ],
            "Ансамбль": [
                {"id": 7, "name": "Ансамбль шпаг", "team": "Театр фехтования"},
                {"id": 8, "name": "Большой ансамбль", "team": "Школа боевых искусств"}
            ]
        }
    else:
        # Получить выступления для мероприятия "тест"
        performances = db.query(Performance).filter(Performance.id_event == test_event.id_event).all()
        
        # Сгруппировать по дисциплинам
        disciplines = {}
        for perf in performances:
            discipline = perf.discipline
            if discipline not in disciplines:
                disciplines[discipline] = []
            
            # Mock данные для команд (пока что)
            team_name = "Театр фехтования" if perf.id_performance % 2 == 1 else "Школа боевых искусств"
            
            disciplines[discipline].append({
                "id": perf.id_performance,
                "name": perf.performance_name,
                "team": team_name
            })

    return templates.TemplateResponse("judge_dashboard.html", {
        "request": request,
        "judge": judge,
        "role_type": role_type,
        "system": system,
        "disciplines": disciplines
    })

@router.get("/judge/{role_type}/{system}/performance/{performance_id}", response_class=HTMLResponse)
async def judge_form(request: Request, role_type: str, system: str, performance_id: int, db: Session = Depends(get_db)):
    """Форма оценки конкретного номера"""
    # Проверить аутентификацию судьи
    judge_id = request.cookies.get("judge_auth")
    if not judge_id:
        return RedirectResponse(url="/", status_code=303)

    judges = load_judges()
    judge = next((j for j in judges if str(j["id"]) == judge_id), None)
    expected_role = f"{role_type}_{system}"
    if not judge or judge["role"] != expected_role:
        return RedirectResponse(url="/", status_code=303)

    # Получить информацию о номере из базы данных
    performance_db = db.query(Performance).filter(Performance.id_performance == performance_id).first()
    if not performance_db:
        return RedirectResponse(url=f"/judge/{role_type}/{system}", status_code=303)

    # Mock данные для команды (пока что)
    team_name = "Театр фехтования" if performance_id % 2 == 1 else "Школа боевых искусств"
    
    performance = {
        "id": performance_db.id_performance,
        "name": performance_db.performance_name,
        "team": team_name,
        "discipline": performance_db.discipline
    }

    template_name = f"judge_{role_type}_{system}.html"
    return templates.TemplateResponse(template_name, {
        "request": request,
        "judge": judge,
        "performance": performance,
        "role_type": role_type,
        "system": system
    })

@router.post("/judge/{role_type}/{system}/score")
async def save_judge_score(
    request: Request,
    role_type: str,
    system: str,
    db: Session = Depends(get_db),
    performance_id: int = Form(...),
    judge_id: int = Form(...)
):
    """Сохранить оценку судьи"""
    # Проверить аутентификацию судьи
    judge_auth_id = request.cookies.get("judge_auth")
    if not judge_auth_id or str(judge_id) != judge_auth_id:
        raise HTTPException(status_code=403, detail="Не авторизован")

    judges = load_judges()
    judge = next((j for j in judges if str(j["id"]) == judge_id), None)
    expected_role = f"{role_type}_{system}"
    if not judge or judge["role"] != expected_role:
        raise HTTPException(status_code=403, detail="Неверная роль")

    # Получить данные формы
    form_data = await request.form()

    # Подготовить данные для сохранения в базу данных
    id_human = judge_id  # Предполагаем, что judge_id соответствует id_human
    id_performance = performance_id

    try:
        if system == "faf":
            if role_type == "technical":
                # Сохранить оценку по технике ФАФ
                score = ScoresTechFaf(
                    id_human=id_human,
                    id_performance=id_performance,
                    criterion_1_1=int(form_data.get("technique", 0)),  # Синхронность техники
                    criterion_1_2=int(form_data.get("safety", 0)),     # Согласованность
                    criterion_1_3=int(form_data.get("precision", 0)),  # Правильность техники
                    criterion_1_4=int(form_data.get("control", 0)),    # Выравнивество
                    criterion_1_5=int(form_data.get("flow", 0)),       # Легкость выполнения
                    criterion_2_1=int(form_data.get("complexity", 0)), # Слаженность
                    criterion_2_2=5,  # Достоверность (заглушка)
                    criterion_2_3=5,  # Качество исполнения (заглушка)
                    criterion_3_1=5,  # Темп (заглушка)
                    criterion_3_2=5,  # Тактическая сложность (заглушка)
                    criterion_3_3=5,  # Координационно-двигательная (заглушка)
                    criterion_3_4=5,  # Поощрение за сложность (заглушка)
                    criterion_3_5=5,  # Разнообразие нападения (заглушка)
                    criterion_3_6=5,  # Разнообразие обороны (заглушка)
                    criterion_3_7=5,  # Разнообразие подготовки (заглушка)
                    criterion_3_8=5   # Общий уровень (заглушка)
                )
                db.add(score)
                
            elif role_type == "artistry":
                # Сохранить оценку по артистике ФАФ
                score = ScoresArtFaf(
                    id_human=id_human,
                    id_performance=id_performance,
                    criterion_1=int(form_data.get("expression", 0)),    # Музыкальность и ритм
                    criterion_2=int(form_data.get("creativity", 0)),    # Артистическое выражение
                    criterion_3=int(form_data.get("harmony", 0)),       # Работа с музыкой
                    criterion_4=int(form_data.get("emotion", 0)),       # Сценическое присутствие
                    criterion_5=int(form_data.get("originality", 0)),   # Характер и эмоции
                    criterion_6=int(form_data.get("interpretation", 0)), # Визуальная эффектность
                    criterion_7=5,  # История/Повествование (заглушка)
                    criterion_8=5,  # Оригинальность идеи (заглушка)
                    criterion_9=5,  # Костюм и реквизит (заглушка)
                    criterion_10=5, # Мизансценирование (заглушка)
                    criterion_11=5, # Переходы и связки (заглушка)
                    criterion_12=5, # Техсредства (заглушка)
                    criterion_13=5  # Общее впечатление (заглушка)
                )
                db.add(score)

        elif system == "naf":
            # Заглушки для НАФ системы
            if role_type == "technical":
                score = ScoresTechNaf(
                    id_human=id_human,
                    id_performance=id_performance,
                    criterion_1_1=float(form_data.get("technique", 0)),
                    criterion_1_2=float(form_data.get("safety", 0)),
                    criterion_1_3=float(form_data.get("precision", 0)),
                    criterion_1_4=float(form_data.get("control", 0)),
                    criterion_1_5=float(form_data.get("flow", 0)),
                    criterion_2_1=float(form_data.get("complexity", 0)),
                    criterion_2_2=1.0,  # Достоверность (заглушка)
                    criterion_2_3=1.0,  # Качество исполнения (заглушка)
                    criterion_3_1=1.0,  # Темп (заглушка)
                    criterion_3_2=1.0,  # Тактическая сложность (заглушка)
                    criterion_3_3=1.0,  # Координационно-двигательная (заглушка)
                    criterion_3_4=1.0,  # Поощрение за сложность (заглушка)
                    criterion_3_5=1.0,  # Разнообразие нападения (заглушка)
                    criterion_3_6=1.0,  # Разнообразие обороны (заглушка)
                    criterion_3_7=1.0,  # Разнообразие подготовки (заглушка)
                    criterion_3_8=1.0   # Общий уровень (заглушка)
                )
                db.add(score)
                
            elif role_type == "artistry":
                score = ScoresArtNaf(
                    id_human=id_human,
                    id_performance=id_performance,
                    criterion_1=float(form_data.get("expression", 0)),
                    criterion_2=float(form_data.get("creativity", 0)),
                    criterion_3=float(form_data.get("harmony", 0)),
                    criterion_4=float(form_data.get("emotion", 0)),
                    criterion_5=float(form_data.get("originality", 0)),
                    criterion_6=float(form_data.get("interpretation", 0)),
                    criterion_7=1.0,  # История/Повествование (заглушка)
                    criterion_8=1.0,  # Оригинальность идеи (заглушка)
                    criterion_9=0.5,  # Костюм и реквизит (заглушка)
                    criterion_10=1.0, # Мизансценирование (заглушка)
                    criterion_11=1.0, # Переходы и связки (заглушка)
                    criterion_12=0.5, # Техсредства (заглушка)
                    criterion_13=1.0  # Общее впечатление (заглушка)
                )
                db.add(score)

        db.commit()
        print(f"Оценка сохранена в базу данных: judge_id={judge_id}, performance_id={performance_id}, system={system}, role={role_type}")

    except Exception as e:
        db.rollback()
        print(f"Ошибка сохранения оценки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сохранения оценки")

    # Перенаправить обратно на дашборд судьи
    return RedirectResponse(url=f"/judge/{role_type}/{system}", status_code=303)