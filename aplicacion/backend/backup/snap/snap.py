import json
import smtplib
import gzip
import os
import tempfile
import threading
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from datetime import datetime
import sys
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(APP_DIR))

try:
    from aplicacion.backend.database.database import (
        SessionLocal, Base, engine,
        Proveedor, StockClasificacion, Producto, StockUnidad,
        VentaRegistro, VentaDetalle, CierreCaja, Ganancia,
        Usuario, UsuarioPerfil, Rol, ActividadUsuario,
        Impuesto, CostoOperativo, ConfiguracionSistema
    )
    print("SNAP: ORM importado correctamente")
except ImportError as e:
    print(f"SNAP: Error importando ORM: {e}")
    sys.exit(1)

DATABASE_PATH = str(APP_DIR / "manoli.db")
ENV_PATH = APP_DIR / ".env"

def load_email_config():
    try:
        if not ENV_PATH.exists():
            print(f"SNAP: Archivo .env no encontrado en: {ENV_PATH}")
            return None, None, None
        
        load_dotenv(dotenv_path=ENV_PATH)
        
        sender_email = os.getenv('SENDER_EMAIL')
        recipient_email = os.getenv('RECIPIENT_EMAIL')
        password = os.getenv('PASSWORD')
        
        if not sender_email or not recipient_email or not password:
            print("SNAP: No se encontraron las variables en el archivo .env")
            return None, None, None
        
        print(f"SNAP: Configuracion cargada desde .env")
        print(f"SNAP: {sender_email} -> {recipient_email}")
        
        return sender_email, recipient_email, password
        
    except Exception as e:
        print(f"SNAP: Error leyendo .env: {e}")
        return None, None, None

def serialize_model_instance(instance):
    if instance is None:
        return None
    
    result = {}
    for column in instance.__table__.columns:
        value = getattr(instance, column.name)
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        elif isinstance(value, bytes):
            value = value.decode('utf-8', errors='ignore')
        result[column.name] = value
    return result

class SnapBackupSystem:
    def __init__(self):
        sender_email, recipient_email, password = load_email_config()
        
        if not sender_email or not recipient_email or not password:
            raise ValueError("No se pudo cargar la configuracion desde .env")
        
        self.gmail_user = sender_email
        self.gmail_app_password = password
        self.recipient_email = recipient_email
        self.database_path = DATABASE_PATH
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        self.control_file = Path(__file__).parent / "last_backup_date.txt"
        
        self.running = True
        self.backup_thread = None
        
        self.models = {
            'proveedores': Proveedor,
            'stock_clasificacion': StockClasificacion,
            'productos': Producto,
            'stock_unidades': StockUnidad,
            'ventas_registro': VentaRegistro,
            'ventas_detalle': VentaDetalle,
            'cierre_caja': CierreCaja,
            'ganancias': Ganancia,
            'usuarios': Usuario,
            'usuarios_perfil': UsuarioPerfil,
            'roles': Rol,
            'actividad_usuarios': ActividadUsuario,
            'impuestos': Impuesto,
            'costos_operativos': CostoOperativo,
            'configuracion_sistema': ConfiguracionSistema
        }
        
        print("SNAP: Sistema inicializado correctamente")
        print(f"DB: {self.database_path}")
        print(f"Control: {self.control_file}")
        print(f"Modelos ORM: {len(self.models)} tablas")
        print("-" * 50)
    
    def get_last_backup_date(self):
        try:
            if self.control_file.exists():
                return self.control_file.read_text().strip()
            return None
        except Exception:
            return None
    
    def save_backup_date(self, date_str):
        try:
            self.control_file.write_text(date_str)
        except Exception as e:
            print(f"SNAP: Error guardando fecha: {e}")
    
    def should_send_today(self):
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        last_backup = self.get_last_backup_date()
        
        if last_backup != today_str and now.hour >= 23:
            return True, "Es hora de envio (23:00+)"
        
        return False, f"Ya enviado hoy ({last_backup})" if last_backup == today_str else "Antes de las 23:00"
    
    def check_database_exists(self):
        if not os.path.exists(self.database_path):
            print(f"SNAP: DB no encontrada: {self.database_path}")
            return False
        return True
    
    def get_table_structure(self, model_class):
        try:
            table = model_class.__table__
            structure = []
            
            for column in table.columns:
                structure.append({
                    "column_name": column.name,
                    "data_type": str(column.type),
                    "not_null": not column.nullable,
                    "primary_key": column.primary_key,
                    "default": str(column.default) if column.default else None
                })
            
            return structure
        except Exception as e:
            print(f"SNAP: Error obteniendo estructura: {e}")
            return []
    
    def export_table_data(self, session, table_name, model_class):
        try:
            print(f"SNAP: Exportando tabla {table_name}...")
            
            records = session.query(model_class).all()
            
            serialized_data = []
            for record in records:
                serialized_record = serialize_model_instance(record)
                if serialized_record:
                    serialized_data.append(serialized_record)
            
            structure = self.get_table_structure(model_class)
            
            return {
                "structure": structure,
                "row_count": len(serialized_data),
                "data": serialized_data
            }
            
        except Exception as e:
            print(f"SNAP: Error exportando tabla {table_name}: {e}")
            return {
                "error": str(e),
                "structure": [],
                "row_count": 0,
                "data": []
            }
    
    def orm_to_json(self):
        if not self.check_database_exists():
            raise FileNotFoundError(f"DB no encontrada: {self.database_path}")
        
        session = SessionLocal()
        
        try:
            db_data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "database_file": os.path.basename(self.database_path),
                    "database_path": self.database_path,
                    "total_tables": len(self.models),
                    "file_size_bytes": os.path.getsize(self.database_path),
                    "backup_system": "SNAP v1.0 ORM",
                    "orm_engine": str(engine.url)
                },
                "tables": {}
            }
            
            total_rows = 0
            
            for table_name, model_class in self.models.items():
                try:
                    table_data = self.export_table_data(session, table_name, model_class)
                    db_data["tables"][table_name] = table_data
                    total_rows += table_data["row_count"]
                    
                except Exception as e:
                    print(f"SNAP: Error en tabla {table_name}: {e}")
                    db_data["tables"][table_name] = {
                        "error": str(e),
                        "structure": [],
                        "row_count": 0,
                        "data": []
                    }
            
            db_data["metadata"]["total_rows"] = total_rows
            print(f"SNAP: Exportadas {len(self.models)} tablas, {total_rows} registros total")
            
            return db_data
            
        finally:
            session.close()
    
    def compress_json(self, data):
        json_string = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        json_bytes = json_string.encode('utf-8')
        return gzip.compress(json_bytes, compresslevel=9)
    
    def cleanup_old_temp_files(self):
        try:
            temp_dir = Path(tempfile.gettempdir()) / "snap_backups"
            if not temp_dir.exists():
                return
            
            import time
            current_time = time.time()
            cleaned_count = 0
            
            for temp_file in temp_dir.glob("snap_*.json.gz"):
                try:
                    if current_time - temp_file.stat().st_mtime > 86400:
                        temp_file.unlink()
                        cleaned_count += 1
                        print(f"SNAP: Limpiado: {temp_file.name}")
                except Exception:
                    pass
            
            if cleaned_count > 0:
                print(f"SNAP: {cleaned_count} archivos antiguos eliminados")
                
        except Exception as e:
            print(f"SNAP: Error en limpieza: {e}")
    
    def create_temp_file(self, data):
        self.cleanup_old_temp_files()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = Path(tempfile.gettempdir()) / "snap_backups"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            dir=temp_dir,
            suffix=f"_manoli_backup_{timestamp}.json.gz",
            prefix="snap_"
        )
        
        compressed_data = self.compress_json(data)
        temp_file.write(compressed_data)
        temp_file.close()
        return temp_file.name
    
    def send_email(self, attachment_path, backup_type="automatico"):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = self.recipient_email
            
            file_size_mb = os.path.getsize(attachment_path) / (1024 * 1024)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db_name = os.path.basename(self.database_path)
            
            msg['Subject'] = f"SNAP Backup {backup_type} - {db_name} - {timestamp}"
            
            body = f"""
SNAP - SISTEMA DE BACKUP AUTOMATICO

Base de datos: {db_name}
Ruta: {self.database_path}
Fecha/Hora: {timestamp}
Tipo: {backup_type}
Tamaño: {file_size_mb:.2f} MB
Compresion: GZIP nivel 9
Sistema: SNAP v1.0 ORM
Tablas: {len(self.models)} modelos ORM

ESTRUCTURA DEL ARCHIVO JSON:
-- backup_info/ (Metadatos del backup)
   -- system (Info del sistema SNAP)
   -- database/ (Detalles de la DB)
   -- export_summary/ (Resumen de exportacion)
-- database_schema/ (Estructura de todas las tablas)
   -- [tabla]/ (Por cada tabla)
      -- columns[] (Definicion de columnas)
      -- record_count (Cantidad de registros)
-- database_content/ (Contenido de todas las tablas)
   -- [tabla]/ (Datos de cada tabla organizados)

Estado: Funcionando correctamente
Proximo envio: Mañana a las 23:00 hrs

Este backup contiene toda la estructura y datos de la base de datos
exportados usando SQLAlchemy ORM en formato JSON super legible,
con indentacion perfecta y organizacion clara por secciones.

JSON formateado con indent=4, claves ordenadas alfabeticamente
Generado automaticamente por SNAP
Sistema integrado con aplicacion principal
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with open(attachment_path, 'rb') as attachment:
                part = MIMEApplication(attachment.read())
                filename = os.path.basename(attachment_path)
                part.add_header('Content-Disposition', f'attachment; filename= {filename}')
                msg.attach(part)
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.gmail_user, self.gmail_app_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"SNAP: Error enviando email: {e}")
            return False
    
    def perform_backup(self, backup_type="automatico"):
        try:
            print(f"\nSNAP: Iniciando backup {backup_type}...")
            start_time = datetime.now()
            
            if not self.check_database_exists():
                print(f"SNAP: Cancelando backup - DB no encontrada")
                return False
            
            print("SNAP: Exportando datos usando SQLAlchemy ORM...")
            db_data = self.orm_to_json()
            
            print("SNAP: Creando archivo comprimido...")
            temp_file_path = self.create_temp_file(db_data)
            
            file_size_mb = os.path.getsize(temp_file_path) / (1024 * 1024)
            print(f"SNAP: Tamaño final: {file_size_mb:.2f} MB")
            
            if file_size_mb > 25:
                print("SNAP: Archivo > 25MB - Gmail podria rechazarlo")
            
            print("SNAP: Enviando email...")
            success = self.send_email(temp_file_path, backup_type)
            
            try:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    print("SNAP: Archivo temporal eliminado")
            except Exception as e:
                print(f"SNAP: Error eliminando temporal: {e}")
            
            if success:
                elapsed = datetime.now() - start_time
                print(f"SNAP: Backup {backup_type} completado en {elapsed.total_seconds():.1f}s")
                
                if backup_type == "automatico programado":
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    self.save_backup_date(today_str)
                    print(f"SNAP: Marcado como enviado: {today_str}")
                
                return True
            else:
                print(f"SNAP: Fallo el backup {backup_type}")
                return False
                
        except Exception as e:
            print(f"SNAP: Error en backup {backup_type}: {e}")
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            return False
    
    def check_and_send_scheduled(self):
        should_send, reason = self.should_send_today()
        now = datetime.now()
        
        print(f"SNAP {now.strftime('%H:%M:%S')} - {reason}")
        
        if should_send:
            print("SNAP: ES HORA DE ENVIAR")
            success = self.perform_backup("automatico programado")
            return success
        
        return False
    
    def scheduler_worker(self):
        print("SNAP: Iniciando verificador horario...")
        
        while self.running:
            try:
                self.check_and_send_scheduled()
                
                for _ in range(360):
                    if not self.running:
                        break
                    time.sleep(10)
                    
            except Exception as e:
                print(f"SNAP: Error en scheduler: {e}")
                time.sleep(60)
    
    def start_background(self):
        if self.backup_thread and self.backup_thread.is_alive():
            print("SNAP: Sistema ya esta corriendo")
            return False
        
        print("SNAP: Iniciando sistema en segundo plano...")
        
        print("SNAP: ENVIO INICIAL AL ARRANCAR")
        initial_success = self.perform_backup("inicial (al arrancar)")
        
        now = datetime.now()
        if now.hour >= 23:
            should_send, reason = self.should_send_today()
            if should_send:
                print(f"\nSNAP: Ya son las {now.hour}:00 hrs - Enviando backup de hoy")
                self.perform_backup("automatico programado")
        
        self.backup_thread = threading.Thread(target=self.scheduler_worker, daemon=True)
        self.backup_thread.start()
        
        print(f"SNAP: Sistema iniciado en segundo plano")
        print(f"SNAP: Verificando cada hora si es tiempo de envio")
        print(f"SNAP: Proximo envio: Hoy a las 23:00 (si no se ha enviado)")
        print(f"SNAP: Destino: {self.recipient_email}")
        
        return initial_success
    
    def stop(self):
        print("SNAP: Deteniendo sistema...")
        self.running = False
        
        if self.backup_thread and self.backup_thread.is_alive():
            self.backup_thread.join(timeout=5.0)
            
        print("SNAP: Sistema detenido")
    
    def manual_backup(self):
        print("SNAP: Backup manual solicitado")
        return self.perform_backup("manual")

_snap_instance = None

def init_snap():
    global _snap_instance
    
    try:
        _snap_instance = SnapBackupSystem()
        return _snap_instance
    except Exception as e:
        print(f"SNAP: Error en inicializacion: {e}")
        return None

def start_snap():
    global _snap_instance
    if _snap_instance:
        return _snap_instance.start_background()
    else:
        print("SNAP: Sistema no inicializado. Llama init_snap() primero.")
        return False

def stop_snap():
    global _snap_instance
    if _snap_instance:
        _snap_instance.stop()

def manual_backup():
    global _snap_instance
    if _snap_instance:
        return _snap_instance.manual_backup()
    else:
        print("SNAP: Sistema no inicializado.")
        return False

def cleanup_all_temp_files():
    try:
        temp_dir = Path(tempfile.gettempdir()) / "snap_backups"
        if not temp_dir.exists():
            print("SNAP: No hay directorio de temporales")
            return 0
        
        cleaned_count = 0
        total_size = 0
        
        for temp_file in temp_dir.glob("snap_*.json.gz"):
            try:
                size = temp_file.stat().st_size
                total_size += size
                temp_file.unlink()
                cleaned_count += 1
                print(f"SNAP: Eliminado: {temp_file.name} ({size/1024/1024:.1f} MB)")
            except Exception as e:
                print(f"SNAP: Error eliminando {temp_file.name}: {e}")
        
        try:
            if not any(temp_dir.iterdir()):
                temp_dir.rmdir()
                print("SNAP: Directorio temporal eliminado")
        except:
            pass
        
        if cleaned_count > 0:
            print(f"SNAP: {cleaned_count} archivos eliminados, {total_size/1024/1024:.1f} MB liberados")
        else:
            print("SNAP: No hay archivos temporales para limpiar")
            
        return cleaned_count
        
    except Exception as e:
        print(f"SNAP: Error en limpieza completa: {e}")
        return 0

def get_snap_instance():
    return _snap_instance

if __name__ == "__main__":
    print("SNAP: Ejecutandose directamente")
    print("SNAP se autoconfigura desde aplicacion/.env")
    print("SNAP usa SQLAlchemy ORM para exportar datos")
    
    try:
        snap = init_snap()
        if snap:
            print("SNAP inicializado correctamente")
            snap.start_background()
        else:
            print("Error inicializando SNAP")
    except KeyboardInterrupt:
        print("\nDetenido por usuario")
        if snap:
            snap.stop()