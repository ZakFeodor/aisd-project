from fastapi import FastAPI, Request, Depends, UploadFile, Form, File
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List
from app.auth import check_credentials, login_user, get_session, check_password, require_user, Session, create_session

BASE_DIR = Path(__file__).resolve().parent.parent
from app.structures import get_row, build_hash_index
from app.structures import SegmentTree, build_segment_tree_from_csv
from app.structures import pagerank
from app.structures import smooth_sort

HASHCACHE = {}
STCACHE = {}
DEFAULT_ARRAY = [1, 5, 3, 9, 11, 6]

app = FastAPI()
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(request=request, name='auth.html')



@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name='register.html')

@app.post("/auth_check", response_class=HTMLResponse)
def auth_page(
        request: Request,
        login: Annotated[str, Form()] = '',
        password: Annotated[str, Form()] = '',
        session: Session = Depends(get_session)
):
    response = RedirectResponse(url=f"/main_page", status_code=303)
    if check_password(login, password, session):
        create_session(response, login)
        return response

    return templates.TemplateResponse(request=request, name='auth.html', context={"error": 'Ошибка пароля или логина'})

@app.post("/register")
def register_user(
        request: Request,
        login: Annotated[str, Form()] = '',
        password: Annotated[str, Form()] = '',
        session: Session = Depends(get_session)
):
    if check_credentials(login, session):
        error = 'Пользователь с этим логином уже существует'
        return templates.TemplateResponse(request=request, name='register.html', context={"error": error})
    response = RedirectResponse(url=f"/main_page", status_code=303)
    create_session(response, login)
    login_user(login, password, session)
    return response

@app.get("/main_page", response_class=HTMLResponse)
def main_page(request: Request):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        request=request,
        name='main_page.html',
        context={"error": error}
    )


@app.post("/main_page/upload")
def upload_file(request: Request, file: UploadFile = File(...)):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    user_dir = BASE_DIR / "uploads" / user
    user_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_dir / file.filename
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return RedirectResponse(url=f"/main_page", status_code=303)

@app.get("/main_page/get_hashmap/get_row", response_class=HTMLResponse)
def hashmap_result(request: Request, transaction_id: str | None = None):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    row = get_row(str(BASE_DIR / "uploads" / user / "Retail_Transactions_Dataset.csv"), int(transaction_id), HASHCACHE.get(user, None))
    if row is None:
        return RedirectResponse(url=f"/main_page?error=Запрашиваемая транзакция не найдена", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name='hashmap.html',
        context={"result": row}
    )

@app.get("/main_page/get_hashmap", response_class=HTMLResponse)
def hashmap(request: Request):
    user = require_user(request)
    file_path = BASE_DIR / "uploads" / user / "Retail_Transactions_Dataset.csv"
    if file_path.exists():
        hashmap = build_hash_index(str(file_path))
        HASHCACHE[user] = hashmap
        return templates.TemplateResponse(
            request=request,
            name='hashmap.html'
        )

    return RedirectResponse(url=f"/main_page?error=Не внесен необходимый файл retail_transactions", status_code=303)

@app.get("/main_page/get_segment_tree/get_result", response_class=HTMLResponse)
def segment_tree_result(request: Request, left: int = 0, right: int = 0):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user

    tree = STCACHE.get(user)
    if tree is None:
        return RedirectResponse(url=f"/main_page?error=Сначала создайте дерево", status_code=303)

    result = tree.query(left, right)

    if hasattr(tree, '_from_csv'):
        return templates.TemplateResponse(
            request=request,
            name='segmenttree.html',
            context={"result": result, "csv_file": "Retail_Transactions_Dataset.csv", "size": tree.n}
        )

    return templates.TemplateResponse(
        request=request,
        name='segmenttree.html',
        context={"result": result, "array": tree.array}
    )


@app.post("/main_page/get_segment_tree/upload")
def segment_tree_upload(request: Request, file: UploadFile = File(...)):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    user_dir = BASE_DIR / "uploads" / user
    user_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_dir / file.filename
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    tree = build_segment_tree_from_csv(str(file_path))
    STCACHE[user] = tree
    return templates.TemplateResponse(
        request=request,
        name='segmenttree.html',
        context={"csv_file": file.filename, "size": tree.n}
    )


@app.get("/main_page/get_segment_tree", response_class=HTMLResponse)
def segment_tree_page(request: Request):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user

    tree = STCACHE.get(user)
    if tree is None:
        file_path = BASE_DIR / "uploads" / user / "Retail_Transactions_Dataset.csv"
        if file_path.exists():
            tree = build_segment_tree_from_csv(str(file_path))
            STCACHE[user] = tree
            return templates.TemplateResponse(
                request=request,
                name='segmenttree.html',
                context={"csv_file": "Retail_Transactions_Dataset.csv", "size": tree.n}
            )
        else:
            tree = SegmentTree(DEFAULT_ARRAY)
            STCACHE[user] = tree
            return templates.TemplateResponse(
                request=request,
                name='segmenttree.html',
                context={"array": DEFAULT_ARRAY}
            )

    if hasattr(tree, '_from_csv'):
        return templates.TemplateResponse(
            request=request,
            name='segmenttree.html',
            context={"csv_file": "Retail_Transactions_Dataset.csv", "size": tree.n}
        )

    return templates.TemplateResponse(
        request=request,
        name='segmenttree.html',
        context={"array": tree.array}
    )


@app.post("/main_page/get_segment_tree", response_class=HTMLResponse)
def segment_tree_set_array(request: Request, array_input: Annotated[str, Form()] = ''):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user

    try:
        arr = [int(x.strip()) for x in array_input.split(',') if x.strip()]
        if not arr:
            raise ValueError
        tree = SegmentTree(arr)
        STCACHE[user] = tree
    except ValueError:
        return RedirectResponse(
            url=f"/main_page?error=Неверный формат массива",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name='segmenttree.html',
        context={"array": arr}
    )

@app.get("/main_page/PageRank/get_result", response_class=HTMLResponse)
def page_rank(request: Request):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user

    return templates.TemplateResponse(
        request=request,
        name='segmenttree.html'
    )

@app.get("/main_page/PageRank", response_class=HTMLResponse)
def page_rank(request: Request):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user

    result = pagerank()

    return templates.TemplateResponse(
        request=request,
        name='pagerank.html',
        context={"result": result}
    )

@app.get("/main_page/smoothsort", response_class=HTMLResponse)
def smoot_sort(request: Request):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user

    return templates.TemplateResponse(
        request=request,
        name='smoothsort.html'
    )

@app.post("/main_page/smoothsort/get_result", response_class=HTMLResponse)
def leonardo_heap_smooth_sort(request: Request, numbers: Annotated[List[int], Form()] = None):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user

    result = smooth_sort(numbers)

    return templates.TemplateResponse(
        request=request,
        name='smoothsort.html',
        context={"result": result}
    )