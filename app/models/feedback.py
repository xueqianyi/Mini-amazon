from flask import current_app as app

class FeedbackToProduct:    
    def __init__(self, pid, sid, uid, date, content, score, image,
                userFirstname=None, userLastname=None, userImage=None, productName=None, productImage=None):
        self.pid = pid
        self.sid = sid
        self.uid = uid
        self.date = date
        self.content = content
        self.score = score
        self.image = image
        
        self.userFirstname = userFirstname
        self.userLastname = userLastname
        self.userImage = userImage
        self.productName = productName
        self.productImage = productImage

    # get the recent feedbacks by a specific user
    @staticmethod
    def get_by_user(uid, limit=6):
        # names represent the sellers
        query = '''
            SELECT fp_pid, fp_sid, fp_uid, fp_date, fp_content, fp_score, fp_image, u_firstname, u_lastname, u_image, p_productName, ps_image
            FROM feedbackProduct
            JOIN Products ON fp_pid = p_pid
            JOIN Users ON fp_sid = u_uid
            JOIN productSeller ON fp_pid = ps_pid AND fp_sid = ps_sid
            WHERE fp_uid = :uid
            ORDER BY fp_date DESC
        '''
        if limit > 0:
            query += 'LIMIT :limit'
            rows = app.db.execute(query, uid=uid, limit=limit)
        else:
            rows = app.db.execute(query, uid=uid)
    
        return [FeedbackToProduct(*row) for row in rows]

    @staticmethod
    def get_by_product(pid,sid):
        # names represent the users
        rows = app.db.execute('''
            SELECT fp_pid, fp_sid, fp_uid, fp_date, fp_content, fp_score, fp_image, u_firstname, u_lastname, u_image
            FROM feedbackProduct, Users
            WHERE fp_pid = :pid AND fp_sid = :sid AND fp_uid = u_uid
            ORDER BY fp_date DESC;
            ''', pid=pid, sid=sid)
        return [FeedbackToProduct(*row) for row in rows]
    
    @staticmethod
    def get_specific(pid,sid,uid):
        rows = app.db.execute('''
            SELECT fp_pid, fp_sid, fp_uid, fp_date, fp_content, fp_score, fp_image
            FROM feedbackProduct
            WHERE fp_pid = :pid AND fp_sid = :sid AND fp_uid = :uid
            ORDER BY fp_date DESC;
            ''', pid=pid, sid=sid, uid=uid)
        return FeedbackToProduct(*rows[0]) if rows else None

    @staticmethod
    def insert_or_update(pid, sid, uid, content, score, image):
        try:
            existing_feedback = FeedbackToProduct.get_specific(pid, sid, uid)
            if existing_feedback:
                # if the record exists, then update it
                app.db.execute('''
                    UPDATE feedbackProduct
                    SET fp_content = :content, fp_score = :score, fp_image = :image, fp_date = CURRENT_TIMESTAMP
                    WHERE fp_pid = :pid AND fp_sid = :sid AND fp_uid = :uid
                ''', pid=pid, sid=sid, uid=uid, content=content, score=score, image=image)
            else:
                # if the record does not exist, then insert it
                app.db.execute('''
                    INSERT INTO feedbackProduct (fp_pid, fp_sid, fp_uid, fp_content, fp_score, fp_image, fp_date)
                    VALUES (:pid, :sid, :uid, :content, :score, :image, CURRENT_TIMESTAMP)
                ''', pid=pid, sid=sid, uid=uid, content=content, score=score, image=image)
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    @staticmethod
    def delete(pid, sid, uid):
        try:
            print("delete", pid, sid, uid)
            app.db.execute('''
                DELETE FROM feedbackProduct
                WHERE fp_pid = :pid AND fp_sid = :sid AND fp_uid = :uid
            ''', pid=pid, sid=sid, uid=uid)
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    
    
class FeedbackToSeller:
    def __init__(self, sid, uid, date, content, score, image,
                 sellerFirstname=None, sellerLastname=None, userFirstname=None, userLastname=None, userImage=None, average_score=None):
        self.sid = sid
        self.uid = uid
        self.date = date
        self.content = content
        self.score = score
        self.image = image
        self.sellerFirstname = sellerFirstname
        self.sellerLastname = sellerLastname
        self.userFirstname = userFirstname
        self.userLastname = userLastname
        self.userImage = userImage
        
    @staticmethod
    def get_specific(sid, uid):
        # names represent the sellers
        query = '''
            SELECT fs.fs_sid, fs.fs_uid, fs.fs_date, fs.fs_content, fs.fs_score, fs.fs_image, 
                s.u_firstname, s.u_lastname, u.u_firstname, u.u_lastname, u.u_image
            FROM feedbackSeller fs
            INNER JOIN users u ON fs.fs_uid = u.u_uid
            INNER JOIN users s ON fs.fs_sid = s.u_uid
            WHERE fs.fs_sid = :sid AND fs.fs_uid = :uid
        '''
        rows = app.db.execute(query, sid=sid, uid=uid)
        return FeedbackToSeller(*rows[0]) if rows else None
    
    # get the recent feedbacks by a specific seller
    @staticmethod
    def get_by_seller(sid, limit=6):
        query = '''
            SELECT fs.fs_sid, fs.fs_uid, fs.fs_date, fs.fs_content, fs.fs_score, fs.fs_image, 
                s.u_firstname, s.u_lastname, u.u_firstname, u.u_lastname, u.u_image
            FROM feedbackSeller fs
            INNER JOIN users u ON fs.fs_uid = u.u_uid
            INNER JOIN users s ON fs.fs_sid = s.u_uid
            WHERE fs.fs_sid = :sid
            ORDER BY fs.fs_date DESC
        '''
        
        if limit > 0:
            query += ' LIMIT :limit'
            rows = app.db.execute(query, sid=sid, limit=limit)
        else:
            rows = app.db.execute(query, sid=sid)

        return [FeedbackToSeller(*row) for row in rows]
    
    
    @staticmethod
    def get_avg_score(sid):
        avg_score_query = '''
            SELECT AVG(fs.fs_score)
            FROM feedbackSeller fs
            WHERE fs.fs_sid = :sid
        '''
        avg_score_result = app.db.execute(avg_score_query, sid=sid)
        avg_score_result = avg_score_result[0][0] if avg_score_result[0][0] else 0
        return round(avg_score_result, 2)
    
    @staticmethod
    def insert_or_update(sid, uid, content, score, image):
        try:
            existing_feedback = FeedbackToSeller.get_specific(sid, uid)
            if existing_feedback:
                # if the record exists, then update it
                app.db.execute('''
                    UPDATE feedbackSeller
                    SET fs_content = :content, fs_score = :score, fs_image = :image, fs_date = CURRENT_TIMESTAMP
                    WHERE fs_sid = :sid AND fs_uid = :uid
                ''', sid=sid, uid=uid, content=content, score=score, image=image)
            else:
                # if the record does not exist, then insert it
                app.db.execute('''
                    INSERT INTO feedbackSeller (fs_sid, fs_uid, fs_content, fs_score, fs_image, fs_date)
                    VALUES (:sid, :uid, :content, :score, :image, CURRENT_TIMESTAMP)
                ''', sid=sid, uid=uid, content=content, score=score, image=image)
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    @staticmethod
    def delete(sid, uid):
        try:
            print("delete", sid, uid)
            app.db.execute('''
                DELETE FROM feedbackSeller
                WHERE fs_sid = :sid AND fs_uid = :uid
            ''', sid=sid, uid=uid)
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            return False