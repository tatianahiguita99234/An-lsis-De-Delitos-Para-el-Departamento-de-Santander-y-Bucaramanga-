import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os
import pickle
from typing import List, Dict, Tuple

class RAGProcessor:
    """
    Procesa datos con RAG 100% gratis (FAISS + Sentence Transformers)
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.embedding_model = None
        self.index = None
        self.chunks = []
        self.df_historicos = None
        self.df_predicciones = None
        
    def initialize(self):
        """Inicializa el modelo de embeddings (gratis, local)"""
        print("🔄 Cargando modelo de embeddings...")
        # Modelo gratis optimizado para español
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ Modelo cargado")
        
    def load_and_process_data(self):
        """Carga CSVs y crea embeddings"""
        try:
            # Cargar CSVs
            historicos_path = os.path.join(self.data_dir, "historicos.csv")
            predicciones_path = os.path.join(self.data_dir, "predicciones.csv")
            
            if os.path.exists(historicos_path):
                self.df_historicos = pd.read_csv(historicos_path)
                print(f"✅ Históricos: {len(self.df_historicos)} registros")
                
            if os.path.exists(predicciones_path):
                self.df_predicciones = pd.read_csv(predicciones_path)
                print(f"✅ Predicciones: {len(self.df_predicciones)} registros")
            
            # Crear chunks de texto de los datos
            self._create_chunks()
            
            # Crear índice FAISS
            self._create_faiss_index()
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def _create_chunks(self):
        """Convierte filas de CSV en chunks de texto"""
        self.chunks = []
        
        # Procesar históricos
        if self.df_historicos is not None:
            # Agrupar por municipio para crear chunks
            for municipio in self.df_historicos['municipio'].unique()[:10]:  # Primeros 10 para demo
                df_mun = self.df_historicos[self.df_historicos['municipio'] == municipio]
                
                # Crear resumen del municipio
                total = len(df_mun)
                chunk_text = f"Municipio: {municipio}. Total de registros: {total}."
                
                # Agregar info por tipo de delito si existe
                if 'tipo_delito' in df_mun.columns:
                    delitos = df_mun['tipo_delito'].value_counts().head(5)
                    chunk_text += f" Principales delitos: {', '.join([f'{d}: {c}' for d, c in delitos.items()])}."
                
                self.chunks.append({
                    'text': chunk_text,
                    'municipio': municipio,
                    'tipo': 'historico',
                    'data': df_mun.to_dict('records')[:100]  # Max 100 registros por chunk
                })
        
        # Procesar predicciones
        if self.df_predicciones is not None:
            for municipio in self.df_predicciones['municipio'].unique()[:10]:
                df_mun = self.df_predicciones[self.df_predicciones['municipio'] == municipio]
                
                chunk_text = f"Predicciones para {municipio}. Total: {len(df_mun)} predicciones."
                
                if 'riesgo' in df_mun.columns:
                    riesgo_alto = len(df_mun[df_mun['riesgo'] == 'alto'])
                    chunk_text += f" Zonas de alto riesgo: {riesgo_alto}."
                
                self.chunks.append({
                    'text': chunk_text,
                    'municipio': municipio,
                    'tipo': 'prediccion',
                    'data': df_mun.to_dict('records')[:100]
                })
        
        print(f"✅ {len(self.chunks)} chunks creados")
    
    def _create_faiss_index(self):
        """Crea índice FAISS con los embeddings"""
        if not self.chunks:
            return
        
        print("🔄 Creando embeddings...")
        
        # Generar embeddings de los textos
        texts = [chunk['text'] for chunk in self.chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Crear índice FAISS
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        print(f"✅ Índice creado con {len(self.chunks)} vectores")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Busca chunks relevantes para una consulta"""
        if self.index is None or not self.chunks:
            return []
        
        # Generar embedding de la consulta
        query_embedding = self.embedding_model.encode([query])
        
        # Buscar en FAISS
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Retornar chunks relevantes
        results = []
        for idx in indices[0]:
            if idx < len(self.chunks):
                results.append(self.chunks[idx])
        
        return results
    
    def get_context_for_query(self, query: str) -> str:
        """Obtiene contexto relevante para una consulta"""
        results = self.search(query, top_k=3)
        
        if not results:
            return "No se encontraron datos relevantes."
        
        context = "DATOS RELEVANTES:\n\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. {result['text']}\n"
            
            # Agregar algunos datos específicos
            if result['data'] and len(result['data']) > 0:
                context += f"   Datos disponibles: {len(result['data'])} registros\n"
        
        return context
    
    def get_summary(self) -> str:
        """Retorna resumen general de los datos"""
        summary = "📊 RESUMEN DEL SISTEMA:\n\n"
        
        if self.df_historicos is not None:
            summary += f"• Datos históricos: {len(self.df_historicos):,} registros\n"
            if 'municipio' in self.df_historicos.columns:
                summary += f"• Municipios con datos: {self.df_historicos['municipio'].nunique()}\n"
        
        if self.df_predicciones is not None:
            summary += f"• Predicciones: {len(self.df_predicciones):,} registros\n"
        
        summary += f"\n• Chunks indexados: {len(self.chunks)}\n"
        summary += f"• Sistema RAG: Activo ✅\n"
        
        return summary
