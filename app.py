import re
import time
import enchant


from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///product_.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Products(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == "POST":
        pid = request.form['pid']
        title = request.form['title']
        product_ = Products(pid=pid, title=title)
        db.session.add(product_)
        db.session.commit()
        with open('word_base.txt', 'r+') as file:
            data = (file.read()).split()
            title_words = set(title.split())
            for word in title_words:
                if word.lower() not in data:
                    file.write(f"{word.lower()}\n")            
    allProducts = Products.query.all()
    return render_template('index.html', allProducts=allProducts)


@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method == "POST":
        pid = request.form['pid']
        title = request.form['title']
        
        product_ = Products.query.filter_by(sno=sno).first()
        product_.title = title
        product_.pid = pid
        db.session.add(product_)
        db.session.commit()
        return redirect("/")

    product_ = Products.query.filter_by(sno=sno).first()
    return render_template('update.html', product_=product_)


@app.route('/delete/<int:sno>')
def delete(sno):
    product_del = Products.query.filter_by(sno=sno).first()
    db.session.delete(product_del)
    db.session.commit()
    return redirect("/")

@app.route('/search/', methods=['GET'])
def search():
    st = time.time()
    pwl = enchant.request_pwl_dict('word_base.txt')
    query_string = request.args.get("query")
    ignore_items = ['and', 'And', 'AND', 'anD', 'AnD', 'aNd', 'aND', '&', 'or', 'OR', 'oR', 'Or', '+', ',', '-']
    all_items_in_string = re.split(r'\W+', query_string)
    items_in_string = list(set([elem.lower() for elem in all_items_in_string if elem not in ignore_items]))

    for idx,item in enumerate(items_in_string):
        x= pwl.check(item)
        if x is False:
            items_in_string[idx] = pwl.suggest(item)[0]

    allProducts = Products.query.all()
    results = []
    for product_ in allProducts:
        pt = set([elem.lower() for elem in re.split(r'\W+', product_.title) if elem not in ignore_items])
        if len(set(items_in_string).intersection(pt)) > 0:
            results.append(product_)

    results = sorted(results, key=lambda x: len(set(items_in_string).intersection(set([elem.lower() for elem in re.split(r'\W+', x.title) if elem not in ignore_items]))), reverse=True)

    top_appearence = []
    for product_ in results:
        pt = set([elem.lower() for elem in re.split(r'\W+', product_.title) if elem not in ignore_items])
        if len(set(items_in_string).intersection(pt)) == len(items_in_string):
            top_appearence.append(product_)

    top_appearence = sorted(top_appearence, key= lambda x: len(x.title))
    results = top_appearence + results[len(top_appearence):]
    et = time.time()
    print(1000*(et-st))
    return render_template('search.html', allProducts=results)
   


if __name__ == '__main__':
    app.run(debug=True, port=7000)
