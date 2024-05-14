# analytics about buyers who have worked with this seller: ratings

from flask import current_app as app
from datetime import datetime
class Buyer_seller:
    def __init__(self, fp_sid, fp_pid, fp_score, fp_image, p_productname, p_category, fp_uid, u_lastname):
        self.sid = fp_sid# processing date
        self.pid = fp_pid
        self.score = fp_score
        self.image = fp_image
        self.productname = p_productname
        self.category = p_category
        self.uid = fp_uid
        self.lastname = u_lastname

    @staticmethod
    def get_score(id): 
        rows = app.db.execute('''
            select fp_sid, fp_pid, fp_score, fp_image, p_productname, p_category, fp_uid, u_lastname from feedbackproduct
            inner join products on products.p_pid = feedbackproduct.fp_pid
            inner join users on users.u_uid = feedbackproduct.fp_uid
            where fp_sid = :sid
            ''', sid=id)
        return [Buyer_seller(*row) for row in rows]

