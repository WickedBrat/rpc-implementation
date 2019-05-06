def is_even(num):
    if num % 2 == 0:
        return True
    else:
        return False


def find_count(s, c):
    return s.count(c)


def find_sum(array):
    result = []

    for element in array:
        for x in element:
            result.append(x)

    return result


def add_account(mongo, account_no, amount):
    mongo.db.bank.insert_one({
        'accountNo': account_no,
        'amount': amount
    })

    return 'Account Created'


def update(mongo, account_no, amount):
    stored_account = mongo.db.bank.find_one({'accountNo': account_no})

    if stored_account:
        mongo.db.bank.update_one({'accountNo': account_no}, {
            '$set': {
                'amount': amount
            }
        })

        return 'Amount Updated'
    else:
        return 'ERROR: Account not found with provided account no'


def get_account(mongo, account_no):
    account = mongo.db.bank.find_one({'accountNo': account_no})

    if account:
        return account['amount']
    else:
        print('ERROR: Account not found')
