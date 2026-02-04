from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
from factorial import bubble_sort, linear_search, binary_search, nested_loops
import time
import os
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

app = Flask(__name__)

# file directory for saving graphs
GRAPHS_DIR = os.path.join('Graphs')
if not os.path.exists(GRAPHS_DIR):
    os.makedirs(GRAPHS_DIR)

# database setup
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

# Analyze algorithm and generate graph endpoint
@app.route('/analyze', methods=['GET'])
def analyze():
    # Get parameters from URL
    algo_name = request.args.get('algo', 'bubble')
    n = int(request.args.get('n', 100))
    steps = int(request.args.get('steps', 10))

    mapping = {
        "bubble": (bubble_sort, "O(n^2)"),
        "linear": (linear_search, "O(n)"),
        "binary": (binary_search, "O(log n)"),
        "nested": (nested_loops, "O(n^2)")
    }
    
    func, complexity = mapping.get(algo_name.split()[0], (bubble_sort, "O(n^2)"))
    
    # this will hold input sizes and their corresponding times
    input_sizes = list(range(n // steps, n + 1, n // steps))
    times = []
    
    start_bench = time.time_ns()
    for size in input_sizes:
        t0 = time.time()
        func(size)
        times.append(time.time() - t0)
    end_bench = time.time_ns()

    # Create the Graph
    plt.figure(figsize=(6, 4))
    plt.plot(input_sizes, times, 'o-')
    plt.title(f"Analysis: {algo_name}")
    plt.xlabel("Input Size")
    plt.ylabel("Time (s)")

    # Create a simple filename using name and timestamp
    timestamp = int(time.time())
    filename = f"{algo_name.replace(' ', '_')}_{timestamp}.png"
    save_path = os.path.join(GRAPHS_DIR, filename)
    
    # Save physical file to Ubuntu disk
    plt.savefig(save_path)
    plt.close()

    # This is the path the frontend uses to show the image
    db_ready_path = f"/Graphs/{filename}"

    return jsonify({
        "algo": algo_name,
        "items": n,
        "steps": steps,
        "start_time": str(start_bench),
        "end_time": str(end_bench),
        "total_time_ms": (end_bench - start_bench) // 1_000_000,
        "time_complexity": complexity,
        "path_to_graph": db_ready_path 
    })

# endpoint to save analysis result to database
@app.route('/save_analysis', methods=['POST'])
def save_analysis():
    data = request.get_json()
    session = Session()
    try:
        # data contains 'path_to_graph' which is just a string path
        new_entry = AnalysisResult(**data)
        session.add(new_entry)
        session.commit()
        return jsonify({"status": "success", "id": new_entry.id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# endpoint to retrieve analysis result from database
@app.route('/retrieve_analysis', methods=['GET'])
def retrieve_analysis():
    analysis_id = request.args.get('id')
    session = Session()
    result = session.query(AnalysisResult).filter_by(id=analysis_id).first()
    session.close()
    
    if not result: 
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "algo": result.algo,
        "items": result.items,
        "steps": result.steps,
        "total_time_ms": result.total_time_ms,
        "time_complexity": result.time_complexity,
        "path_to_graph": result.path_to_graph
    })

if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)