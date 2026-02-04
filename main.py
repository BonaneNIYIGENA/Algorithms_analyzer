from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus # For the password fix
from factorial import bubble_sort, linear_search, binary_search, nested_loops
import time
import io
import base64
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

app = Flask(__name__)

# --- 1. SQLALCHEMY SETUP ---
password = quote_plus("rwigema@336#")
engine = create_engine(f"mysql+pymysql://root:{password}@localhost:3306/algorithm_analysis")
Base = declarative_base()


class AnalysisResult(Base):
    __tablename__ = 'algo_analysis'
    id = Column(Integer, primary_key=True, autoincrement=True)
    algo = Column(String(50))
    items = Column(Integer)
    steps = Column(Integer)
    start_time = Column(String(100))
    end_time = Column(String(100))
    total_time_ms = Column(Integer)
    time_complexity = Column(String(20))
    path_to_graph = Column(Text)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# --- 2. THE ANALYZE ENDPOINT (The Missing Link) ---
@app.route('/analyze', methods=['GET'])
def analyze():
    algo_name = request.args.get('algo', 'bubble sort')
    n = int(request.args.get('n', 100))
    steps = int(request.args.get('steps', 10))

    mapping = {
        "bubble": (bubble_sort, "O(n^2)"),
        "linear": (linear_search, "O(n)"),
        "binary": (binary_search, "O(log n)"),
        "nested": (nested_loops, "O(n^2)")
    }
    
    # Get the function based on query param
    func, complexity = mapping.get(algo_name.split()[0], (bubble_sort, "O(n^2)"))
    
    # Analyze and Graph
    input_sizes = list(range(n // steps, n + 1, n // steps))
    times = []
    
    start_bench = time.time_ns()
    for size in input_sizes:
        t0 = time.time()
        func(size)
        times.append(time.time() - t0)
    end_bench = time.time_ns()

    # Create Graph to Base64
    plt.figure(figsize=(6, 4))
    plt.plot(input_sizes, times, 'o-')
    plt.title(f"Analysis of {algo_name}")
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return jsonify({
        "algo": algo_name,
        "items": n,
        "steps": steps,
        "start_time": start_bench,
        "end_time": end_bench,
        "total_time_ms": (end_bench - start_bench) // 1_000_000,
        "time_complexity": complexity,
        "path_to_graph": f"data:image/png;base64,{img_base64}"
    })


# --- 3. SAVE & RETRIEVE ENDPOINTS (Your existing code) ---
@app.route('/save_analysis', methods=['POST'])
def save_analysis():
    data = request.get_json()
    session = Session()
    try:
        new_entry = AnalysisResult(**data)
        session.add(new_entry)
        session.commit()
        return jsonify({"status": "success", "id": new_entry.id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# 4. Retrieve the analysis saved by using its ID
@app.route('/retrieve_analysis', methods=['GET'])
def retrieve_analysis():
    analysis_id = request.args.get('id')
    session = Session()
    result = session.query(AnalysisResult).filter_by(id=analysis_id).first()
    session.close()
    if not result: 
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "algo": result.algo, "items": result.items, "steps": result.steps,
        "total_time_ms": result.total_time_ms, "time_complexity": result.time_complexity,
        "path_to_graph": result.path_to_graph
    })


if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)