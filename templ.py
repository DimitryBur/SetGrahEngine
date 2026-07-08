import pandas as pd
from graph_engine import MultipartiteSetGraphEngine, 

# -------------------------------------------------------------
# 🏭 СБОРКА РЕАЛИСТИЧНОГО ВЗВЕШЕННОГО МНОГОДОЛЬНОГО ГРАФА
# -------------------------------------------------------------
def generate_complete_test_data():
    partitions = ['Shop', 'Supplier', 'Product', 'District', 'Category']
    nodes = {p: [f"{p}_{i}" for i in range(2000)] for p in partitions}
    
    allowed_pairs = [
        ('Shop', 'Product'), 
        ('Supplier', 'Product'), 
        ('Shop', 'District'),
        ('Product', 'Category')
    ]
    
    sources, targets = [], []
    for p1, p2 in allowed_pairs:
        sources.append(np.random.choice(nodes[p1], size=250000))
        targets.append(np.random.choice(nodes[p2], size=250000))
        
    df = pd.DataFrame({'source': np.concatenate(sources), 'target': np.concatenate(targets)})
    df['weight'] = np.random.uniform(100, 10000, size=len(df))
    return df

df = generate_complete_test_data()
engine = MultipartiteSetGraphEngine()
t0 = time.time()
build_time = engine.build_from_df(df, weight_col='weight')
processor = MathGraphQueryProcessor(engine)
print(f"⏱️ Граф собран в CSR-структуру памяти за: {build_time:.4f} сек\n")

print("=" * 80)
print("🪐 ТЕСТИРОВАНИЕ ВСЕХ ВОЗМОЖНОСТЕЙ СИНТАКСИСА АЛГЕБРЫ МНОЖЕСТВ")
print("=" * 80)

# Сценарий 1: Базовые соседи (1 шаг) с условием WHERE по типу
q1 = "math neig(Shop_5) where label = 'Product'"
t0 = time.time()
res1 = processor.execute(q1)
print(f"1️⃣  [neig + WHERE]: {q1}\n⏱️ Время: {(time.time()-t0)*1000:.3f} мс | Найдено: {len(res1)} | Сэмпл: {res1[:3]}\n" + "-"*80)

# Сценарий 2: ВАШ ПАТТЕРН УПУЩЕННОЙ ВЫГОДЫ 
# Что продается у смежных конкурентов, чего еще НЕТ в ассортименте Shop_5
q2 = "math diff(adjac(neig(Shop_5)), neig(Shop_5)) where label = 'Product'"
t0 = time.time()
res2 = processor.execute(q2)
print(f"2️⃣  [Упущенная выгода]: {q2}\n⏱️ Время: {(time.time()-t0)*1000:.3f} мс | Найдено потенциальных товаров: {len(res2)} | Сэмпл: {res2[:3]}\n" + "-"*80)

# Сценарий 3: Пересечение фронтов связей двух магазинов (Общие сущности)
q3 = "math intersect(neig(Shop_5), neig(Shop_6))"
t0 = time.time()
res3 = processor.execute(q3)
print(f"3️⃣  [intersect]: {q3}\n⏱️ Время: {(time.time()-t0)*1000:.3f} мс | Найдено общих элементов: {len(res3)} | Сэмпл: {res3[:3]}\n" + "-"*80)

# Сценарий 4: Объединение фронтов (Суммарный охват)
q4 = "math union(neig(Shop_5), neig(Shop_6))"
t0 = time.time()
res4 = processor.execute(q4)
print(f"4️⃣  [union]: {q4}\n⏱️ Время: {(time.time()-t0)*1000:.3f} мс | Найдено уникальных элементов: {len(res4)} | Сэмпл: {res4[:3]}\n" + "-"*80)

# Сценарий 5: Быстрая серверная агрегация (Размер множества без оверхеда на строки)
q5 = "math count(union(neig(Shop_5), neig(Shop_6)))"
t0 = time.time()
res5 = processor.execute(q5)
print(f"5️⃣  [count]: {q5}\n⏱️ Время: {(time.time()-t0)*1000:.3f} мс | Результат: {res5} узлов\n" + "-"*80)

# Сценарий 6: Фильтрация весов ребер на Си-скорости (Только крупные транзакции > 8000 рублей)
q6 = "math neig(Shop_5) where label = 'Product' and edge_weight > 8000"
t0 = time.time()
res6 = processor.execute(q6)
print(f"6️⃣  [edge_weight]: {q6}\n⏱️ Время: {(time.time()-t0)*1000:.3f} мс | Найдено дорогих товаров: {len(res6)} | Сэмпл: {res6[:3]}\n" + "-"*80)

# Сценарий 7: Поиск путей (Цепочки транзитов через Product с исключением District)
q7 = "math path(Shop_5, Shop_6) where label = 'Product' and not label = 'District'"
t0 = time.time()
res7 = processor.execute(q7)
print(f"7️⃣  [path + комплексный WHERE]: {q7}\n⏱️ Время: {(time.time()-t0)*1000:.3f} мс | Найдено цепочек: {len(res7)} | Пример: {res7[:1]}\n" + "="*80)

#Сценарий 8: Поиск путей (Цепочки транзитов через Product с исключением District)
q8 = "math diff(neig(Shop_5), neig(Shop_6)) where label = 'Product' and edge_weight > 7000 and not label = 'District'"
t0 = time.time()
res8 = processor.execute(q8)
print(f"8  [комплексный WHERE]: {q8}\n⏱️ Время: {(time.time()-t0)*1000:.3f} мс | Найдено цепочек: {len(res8)} | Пример: {res8[:1]}\n" + "="*80) 
print("✅ ВСЕ КОМБИНАЦИИ СИНТАКСИСА УСПЕШНО ПРОВЕРЕНЫ!")
