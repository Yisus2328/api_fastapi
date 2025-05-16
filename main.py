from fastapi import FastAPI, APIRouter, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from database import get_conexion
import MySQLdb






# codigo para iniciar la app - debe estar en el cd fastapi
# venv\Scripts\activate
# uvicorn main:app --reload --port 8001
# http://127.0.0.1:8001/producto/ - se debe cargar si o si esta ruta - para cargar todos los productos de la BD
# http://127.0.0.1:8001/producto/P001 se debe cargar si o si esta ruta - para cargar producto por el I
# http://127.0.0.1:8001/producto/agregar_prod se debe cargar si o si esta ruta  y agregar desde postman
# http://127.0.0.1:8001/producto/P002 se debe cargar el id del producto (existente) para probar el actualizar
# http://127.0.0.1:8001/producto/P002 se debe cargar si o si esta ruta (variable)  y para probar eliminar desde postman

app = FastAPI()
router = APIRouter(
    prefix="/producto",
    tags=["Producto"]
)

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@router.get("/")
def obtener_productos():
    try:
        cone = get_conexion()
        if cone:
            cursor = cone.cursor()
            cursor.execute("SELECT id_producto, nombre, descripcion, precio, marca, categoria, stock FROM PRODUCTO")
            productos = []
            for id_producto, nombre, descripcion, precio, marca, categoria, stock in cursor:
                productos.append({
                    "id_producto": id_producto,
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "precio": precio,
                    "marca": marca,
                    "categoria": categoria,
                    "stock": stock
                })
            cursor.close()
            cone.close()
            return productos
        else:
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))




@router.get("/{id_producto}")
def obtener_producto(id_producto: str):
    try:
        cone = get_conexion()
        if cone:
            cursor = cone.cursor()
            cursor.execute("SELECT nombre, descripcion, precio, marca, categoria, stock FROM PRODUCTO WHERE id_producto = %s", (id_producto,))
            producto = cursor.fetchone()
            cursor.close()
            cone.close()
            if producto:
                return {
                    "id_producto": id_producto,
                    "nombre": producto[0],
                    "descripcion": producto[1],
                    "precio": producto[2],
                    "marca": producto[3],
                    "categoria": producto[4],
                    "stock": producto[5]  # <-- Accedemos al stock desde la tupla 'producto'
                }
            else:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
        else:
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))



@router.post("/agregar_prod")
def agregar_producto(
    id_producto: str = Body(...),
    nombre: str = Body(...),
    precio: int = Body(...),
    marca: str = Body(...),
    categoria: str = Body(...),
    stock: int = Body(...),
    descripcion: str | None = Body(default=None)
):
    try:
        cone = get_conexion()
        if cone:
            cursor = cone.cursor()
            cursor.execute("""
                INSERT INTO producto (id_producto, nombre, descripcion, precio, marca, categoria, stock)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id_producto, nombre, descripcion, precio, marca, categoria, stock))
            cone.commit()
            cursor.close()
            cone.close()
            return {"mensaje": f"Producto {nombre} agregado con éxito con ID: {id_producto}"}
        else:
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    except MySQLdb.Error as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar el producto: {e}")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))



@router.put("/{id_producto}")
def actualizar_producto(id_producto: str, producto: dict = Body(...)):
    try:
        cone = get_conexion()
        if cone:
            cursor = cone.cursor()
            nombre = producto.get("nombre")
            descripcion = producto.get("descripcion")
            precio = producto.get("precio")
            marca = producto.get("marca")
            categoria = producto.get("categoria")
            stock = producto.get("stock")

            consulta = "UPDATE PRODUCTO SET "
            valores = []

            if nombre is not None:
                consulta += "nombre = %s, "
                valores.append(nombre)
            if descripcion is not None:
                consulta += "descripcion = %s, "
                valores.append(descripcion)
            if precio is not None:
                consulta += "precio = %s, "
                valores.append(precio)
            if marca is not None:
                consulta += "marca = %s, "
                valores.append(marca)
            if categoria is not None:
                consulta += "categoria = %s, "
                valores.append(categoria)
            if stock is not None:
                consulta += "stock = %s, "
                valores.append(stock)

            # Eliminar la coma final si se agregaron campos para actualizar
            if valores:
                consulta = consulta[:-2]

            consulta += " WHERE id_producto = %s"
            valores.append(id_producto)

            cursor.execute(consulta, valores)
            cone.commit()
            filas_afectadas = cursor.rowcount
            cursor.close()
            cone.close()

            if filas_afectadas > 0:
                return {"mensaje": f"Producto con ID {id_producto} actualizado con éxito"}
            else:
                raise HTTPException(status_code=404, detail=f"Producto con ID {id_producto} no encontrado")
        else:
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    except MySQLdb.Error as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el producto: {e}")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.delete("/{id_producto}")
def eliminar_producto(id_producto: str):
    try:
        cone = get_conexion()
        if cone:
            cursor = cone.cursor()
            cursor.execute("DELETE FROM PRODUCTO WHERE id_producto = %s", (id_producto,))
            filas_afectadas = cursor.rowcount
            cone.commit()
            cursor.close()
            cone.close()

            if filas_afectadas > 0:
                return {"mensaje": f"Producto con ID {id_producto} eliminado con éxito"}
            else:
                raise HTTPException(status_code=404, detail=f"Producto con ID {id_producto} no encontrado")
        else:
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    except MySQLdb.Error as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el producto: {e}")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


app.include_router(router)