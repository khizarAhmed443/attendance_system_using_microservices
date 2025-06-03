from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(os.path.dirname(basedir), 'instance', 'classes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Class Model
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

# Create database tables
with app.app_context():
    db.create_all()
    print(f"Database initialized at: {db_path}")

@app.route('/api/classes', methods=['GET', 'POST'])
def handle_classes():
    if request.method == 'GET':
        try:
            classes = Class.query.all()
            return jsonify([cls.to_dict() for cls in classes])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data or 'name' not in data:
                return jsonify({'error': 'Class name is required'}), 400

            # Check if class already exists
            existing_class = Class.query.filter_by(name=data['name']).first()
            if existing_class:
                return jsonify({'error': 'Class already exists'}), 400

            new_class = Class(
                name=data['name'],
                description=data.get('description', '')
            )
            db.session.add(new_class)
            db.session.commit()
            return jsonify(new_class.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/api/classes/<int:class_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_class(class_id):
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404

    if request.method == 'GET':
        return jsonify(class_obj.to_dict())

    if request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            if 'name' in data:
                # Check if new name already exists
                existing = Class.query.filter_by(name=data['name']).first()
                if existing and existing.id != class_id:
                    return jsonify({'error': 'Class name already exists'}), 400
                class_obj.name = data['name']

            if 'description' in data:
                class_obj.description = data['description']

            db.session.commit()
            return jsonify(class_obj.to_dict())

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    if request.method == 'DELETE':
        try:
            db.session.delete(class_obj)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5004, debug=True) 