# Fast Multipartite Graph Set-Algebra Engine
A high-performance discrete graph analysis engine built with Python, NumPy, and SciPy. This project leverages Compressed Sparse Row (CSR) matrix representations to perform rapid set-algebra operations and pathfinding on large-scale multipartite graphs. It includes a built-in domain-specific language (DSL) parser to execute complex graph queries with a SQL-like where filtering layer.
## Key Features

* CSR Matrix Backend: Efficient memory layout and lightning-fast neighbor lookups via SciPy's sparse matrices.
* Vectorized Operations: Node filtering, intersections, and unions are executed using highly optimized NumPy functions (isin, intersect1d, union1d).
* Graph Set-Algebra DSL: A custom query language that supports operations like neig(), adjac(), union(), intersect(), diff(), and count().
* Dynamic Conditional Filtering: Filter runtime graph slices by node type labels and edge weight thresholds directly within the query.
* Optimized Pathfinding: Fast retrieval of intermediate 2-step and 3-step paths between specific entities.

## Architecture Overview## 1. MultipartiteSetGraphEngine
This core class transforms a standard tabular pandas DataFrame into a bidirectional graph inside a single unified CSR matrix. Node types (e.g., Shop, Product, Supplier) are dynamically parsed out of prefixes (e.g., Shop_5) and stored in a specialized partitions array for O(1) mask indexing.
## 2. MathGraphQueryProcessor
A recursive query interpreter that parses custom string expressions starting with the math prefix. It decouples the core graph mathematics from network overhead, executing logic layers at native C-speeds.
------------------------------
## Query Syntax (DSL) Reference
Every query must begin with the math prefix, followed by a set expression and an optional where clause.
## Core Set Functions

| Function | Description | Example |
|---|---|---|
| neig(X) | Returns the immediate (1-hop) neighbors of set X. | math neig(Shop_5) |
| adjac(X) | Returns the 2-hop neighbors (neighbors of neighbors) of set X. | math adjac(Shop_5) |
| intersect(A, B) | Computes the intersection of set A and set B. | math intersect(neig(Shop_5), neig(Shop_6)) |
| union(A, B) | Computes the union of set A and set B. | math union(neig(Shop_5), neig(Shop_6)) |
| diff(A, B) | Computes the set difference (A \ B). Useful for gap analysis. | math diff(neig(Shop_5), neig(Shop_6)) |
| count(X) | Fast server-side aggregation returning the size of the set. | math count(union(neig(Shop_1), neig(Shop_2))) |
| path(A, B) | Finds transition paths up to 3 hops between nodes A and B. | math path(Shop_5, Shop_6) |

## Conditional Filters (where clause)
You can append conditional statements using the where keyword:

* label = 'PartitionName' — Include only specific node types.
* not label = 'PartitionName' — Exclude specific node types.
* edge_weight > value — Filter graph relationships based on minimal connection weights.

------------------------------
## Installation & Requirements
Ensure you have Python 3.8+ installed along with the required scientific computing libraries:

pip install numpy pandas scipy

------------------------------
## Quick Start Example

import pandas as pd

from graph_engine import MultipartiteSetGraphEngine, MathGraphQueryProcessor

# 1. Prepare sample transactional 

data = {
    'source': ['Shop_1', 'Shop_1', 'Supplier_1', 'Shop_2'],
    'target': ['Product_A', 'Product_B', 'Product_A', 'Product_B'],
    'weight': [5000.0, 12000.0, 9500.0, 3000.0]}

df = pd.DataFrame(data)

# 2. Initialize and build the graph engineengine = MultipartiteSetGraphEngine()

engine.build_from_df(df, source_col='source', target_col='target', weight_col='weight')

# 3. Instantiate the DSL processorprocessor = MathGraphQueryProcessor(engine)

# 4. Execute an "Assortment Gap" / Unused Potential query
# Finds what products similar shops sell, which Shop_1 does NOT sell 

yet.query = "math diff(adjac(neig(Shop_1)), neig(Shop_1)) where label = 'Product'"result = processor.execute(query)

print("Recommended Products for Shop_1:", result)

## Performance Benchmarks
When tested against a multipartite synthetic dataset containing 1,000,000 edges across various entity types (Shops, Suppliers, Products, Districts, Categories), execution times demonstrate high efficiency:

* Graph Build Time: ~0.70 seconds (1M records into CSR mapping) (p. 8).
* 1-Hop Neighbor Lookup: ~0.70 ms (p. 8).
* Assortment Gap Analysis (diff(adjac(...))): ~30.00 ms (p. 8).
* Set Intersection: ~0.43 ms (p. 8).
* Complex Multi-hop Pathfinding: ~16.28 ms (p. 8).
