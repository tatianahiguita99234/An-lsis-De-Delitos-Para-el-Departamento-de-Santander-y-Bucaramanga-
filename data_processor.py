import pandas as pd
import os
from typing import List, Dict, Any
import json

class DataProcessor:
    """
    Procesa los datos históricos y de predicciones para alimentar el chatbot
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.historicos_df = None
        self.predicciones_df = None
        self.context_data = None
        
    def load_data(self) -> bool:
        """Carga los archivos CSV de datos"""
        try:
            historicos_path = os.path.join(self.data_dir, "historicos.csv")
            predicciones_path = os.path.join(self.data_dir, "predicciones.csv")
            
            if os.path.exists(historicos_path):
                self.historicos_df = pd.read_csv(historicos_path)
                print(f"✅ Datos históricos cargados: {len(self.historicos_df)} registros")
            
            if os.path.exists(predicciones_path):
                self.predicciones_df = pd.read_csv(predicciones_path)
                print(f"✅ Predicciones cargadas: {len(self.predicciones_df)} registros")
            
            # Generar contexto para el LLM
            self._generate_context()
            return True
            
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return False
    
    def _generate_context(self):
        """Genera un contexto resumido de los datos para el LLM"""
        context = {
            "descripcion": "Datos de seguridad y criminalidad de Santander, Colombia",
            "fuente": "Policía Nacional de Colombia - Gobernación de Santander",
            "municipios": 87
        }
        
        # Información de datos históricos
        if self.historicos_df is not None:
            context["historicos"] = {
                "total_registros": len(self.historicos_df),
                "columnas": list(self.historicos_df.columns),
                "periodo": self._get_date_range(self.historicos_df),
                "estadisticas_basicas": self._get_basic_stats(self.historicos_df)
            }
        
        # Información de predicciones
        if self.predicciones_df is not None:
            context["predicciones"] = {
                "total_registros": len(self.predicciones_df),
                "columnas": list(self.predicciones_df.columns),
                "estadisticas_basicas": self._get_basic_stats(self.predicciones_df)
            }
        
        self.context_data = context
    
    def _get_date_range(self, df: pd.DataFrame) -> Dict[str, str]:
        """Obtiene el rango de fechas del dataframe"""
        date_columns = df.select_dtypes(include=['datetime64']).columns
        if len(date_columns) > 0:
            date_col = date_columns[0]
            return {
                "inicio": str(df[date_col].min()),
                "fin": str(df[date_col].max())
            }
        return {}
    
    def _get_basic_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Obtiene estadísticas básicas del dataframe"""
        stats = {}
        
        # Columnas numéricas
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats["numericas"] = {
                col: {
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "promedio": float(df[col].mean()),
                    "total": float(df[col].sum())
                }
                for col in numeric_cols[:5]  # Solo las primeras 5 columnas
            }
        
        # Columnas categóricas
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            stats["categoricas"] = {
                col: df[col].value_counts().head(5).to_dict()
                for col in categorical_cols[:3]  # Solo las primeras 3 columnas
            }
        
        return stats
    
    def get_context_string(self) -> str:
        """Retorna el contexto como string formateado para el LLM"""
        if self.context_data is None:
            return "No hay datos disponibles."
        
        context_str = f"""
CONTEXTO DE DATOS DEL OBSERVATORIO DE SEGURIDAD DE SANTANDER:

Descripción: {self.context_data['descripcion']}
Fuente: {self.context_data['fuente']}
Cobertura: {self.context_data['municipios']} municipios

"""
        
        if "historicos" in self.context_data:
            hist = self.context_data["historicos"]
            context_str += f"""
DATOS HISTÓRICOS:
- Total de registros: {hist['total_registros']:,}
- Columnas disponibles: {', '.join(hist['columnas'])}
"""
            if hist.get('periodo'):
                context_str += f"- Período: {hist['periodo'].get('inicio', 'N/A')} a {hist['periodo'].get('fin', 'N/A')}\n"
        
        if "predicciones" in self.context_data:
            pred = self.context_data["predicciones"]
            context_str += f"""
PREDICCIONES GENERADAS:
- Total de predicciones: {pred['total_registros']:,}
- Variables predictivas: {', '.join(pred['columnas'])}
"""
        
        return context_str
    
    def query_data(self, query: str) -> Dict[str, Any]:
        """
        Realiza consultas específicas sobre los datos
        Útil para responder preguntas puntuales del usuario
        """
        results = {}
        
        # Aquí puedes agregar lógica específica para consultas comunes
        # Por ejemplo: "cuántos delitos en 2024", "municipio más peligroso", etc.
        
        return results
    
    def get_summary(self) -> str:
        """Retorna un resumen general de los datos"""
        if self.context_data is None:
            return "No hay datos cargados."
        
        summary = "📊 RESUMEN DE DATOS:\n\n"
        
        if "historicos" in self.context_data:
            hist = self.context_data["historicos"]
            summary += f"✅ Datos Históricos: {hist['total_registros']:,} registros\n"
        
        if "predicciones" in self.context_data:
            pred = self.context_data["predicciones"]
            summary += f"✅ Predicciones: {pred['total_registros']:,} registros\n"
        
        summary += f"\n🗺️ Cobertura: {self.context_data['municipios']} municipios de Santander"
        
        return summary
