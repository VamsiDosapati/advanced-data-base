from flask import Flask, Response, request, jsonify
from py2neo import Graph, Node, Relationship

app = Flask(__name__)

uri = "neo4j+s://e2adcd83.databases.neo4j.io"
pwd = "cGRqnUCdiE1krn3bLvoOcEDFdeSvZeQIMyhSDU0ADEk"

graph = Graph(uri, password=pwd)

@app.route('/')
def index():
    return "Hello, World!"
@app.route('/chars', methods=['POST'])
def insert_character():
    try:
        character_data = request.get_json()
        character_name = character_data['name']

        tx = graph.begin()
        result = tx.run(
            "MATCH (c:Characters {name: $name}) RETURN c",
            name=character_name
        )

        if result.data():
            tx.rollback()
            return jsonify({'message': 'Character with the same name already exists'})

        tx.run(
            "CREATE (c:Characters {name: $name, height: $height, mass: $mass, "
            "skin_colors: $skin_colors, hair_colors: $hair_colors, eye_colors: $eye_colors, "
            "birth_year: $birth_year, gender: $gender, homeworld: $homeworld, species: $species})",
            name=character_name,
            height=character_data.get('height'),
            mass=character_data.get('mass'),
            skin_colors=character_data.get('skin_colors'),
            hair_colors=character_data.get('hair_colors'),
            eye_colors=character_data.get('eye_colors'),
            birth_year=character_data.get('birth_year'),
            gender=character_data.get('gender'),
            homeworld=character_data.get('homeworld'),
            species=character_data.get('species')
        )

        tx.commit()
        return jsonify({'message': 'Character inserted successfully'})
    except Exception as e:
        return jsonify({'message': 'Character not inserted. An error occurred: ' + str(e)})



@app.route('/chars/<string:fname>', methods=['DELETE'])
def delete_character(fname):
    
    delete_character_node = graph.nodes.match("Characters", name=fname).first()

    if delete_character_node:
        
        graph.delete(delete_character_node)

        return jsonify({'message': 'Character deletedd successfully'})
    else:
        return jsonify({'message': 'Character not found'})
    
@app.route('/chars', methods=['GET'])
def get_all_characters():
    all_character_nodes = graph.nodes.match("Characters")

    characters = []
    for node in all_character_nodes:
        characters.append(dict(node))

    return jsonify({'characters': characters})
@app.route('/chars/<string:fname>', methods=['PATCH'])
def update_character(fname):
    character_node = graph.nodes.match("Characters", name=fname).first()
    print(character_node)
    if character_node:
        json_data = request.get_json()
        print("Request payload:", json_data)

        if 'name' in json_data:
            character_node["name"] = json_data['name']
        if 'hair_colors' in json_data:
            character_node["hair_colors"] = json_data['hair_colors']
        if 'height' in json_data:
            character_node["height"] = json_data['height']
        if 'birth_year' in json_data:
            character_node["birth_year"] = json_data['birth_year']

        graph.push(character_node)

        return jsonify({'message': 'Character updated successfully'})
    else:
        return jsonify({'message': 'Character not found'})

@app.route('/chars/<string:fname>', methods=['GET'])
def get_character(fname):
    existing_character_node = graph.nodes.match("Characters", name=fname).first()

    if existing_character_node:
        return jsonify(dict(existing_character_node))
    else:
        return jsonify({'message': 'Character not found'})

if __name__ == '__main__':
    app.debug=False
    app.run()