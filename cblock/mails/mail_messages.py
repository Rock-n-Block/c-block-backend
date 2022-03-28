EMAIL_TEXTS = {
    'lastwill': {
        'reminder': {
          'title': 'Reminder to confirm live status',
          'body': """
Hello! 

We would like to remind you to confirm your “live” status for the contract. 
Contract will be executed if no confirmation during the next {days} days. 
You can see the contract here: app.c-block.io/my-contracts 
If you have any questions please contact c-support@bitflex.app

Best wishes, Bitflex Team
          """
        },
        'triggered': {
            'title': 'Our condolences - the owner has passed away',
            'body': """
Hello! 

In accordance with the Will contract created on С-block platform by "{owner_address}", 
Funds will be transferred to your address {receiver_address}.
To speed up the process, visit the app.c-block.io/earn and press Transfer button next to the your address. 
Otherwise, you have to wait until other user performs this action.
If you have any questions, please contact c-support@bitflex.app

Best wishes, Bitflex Team
          """
        },
        'transferred_from_owner': {
          'title': 'Funds were transferred',
          'body': """
Hello! 

In accordance with the contract created on С-block platform, 
Funds were transferred to backup addresses: "{backup_addresses}": {link_tx}
If you have any questions, please contact c-support@bitflex.app

Best wishes, Bitflex Team"""
        },
        'transferred_to_heirs': {
          'title': 'Funds were transferred',
          'body': """
Hello! 

In accordance with the Will contract created on С-block platform by "{owner_address}", 
Funds have been transferred to your address: "{receiver_address}": {link_tx}
If you have any questions, please contact c-support@bitflex.app

Best wishes, Bitflex Team
          """
        },
    },
    'lostkey': {
        'reminder': {
          'title': 'Reminder to confirm active status',
          'body': """
 Hello! 
 
 We would like to remind you to confirm your “active” status for the contract. 
 Contract will be executed if no confirmation during the next {days} days. 
 You can see the contract here: app.c-block.io/my-contracts 
 If you have any questions please contact c-support@bitflex.app

Best wishes, Bitflex Team
        """
        },
        'triggered': {
            'title': 'You lost the access to your wallet',
            'body': """
Hello! 

In accordance with the Lost Key contract created on С-block platform by "{owner_address}", 
Funds will be transferred to your address "{receiver_address}".
To speed up the process, visit the app.c-block.io/earn and press Transfer button next to the your address. 
Otherwise, you have to wait until other user performs this action.
If you have any questions, please contact c-support@bitflex.app

Best wishes, Bitflex Team
          """
        },
        'transferred_from_owner': {
          'title': 'Funds were transferred',
          'body': """
Hello! 

In accordance with the contract created on С-block platform, 
Funds have been transferred to backup addresses: "{backup_addresses}": {link_tx}
If you have any questions, please contact c-support@bitflex.app

Best wishes, Bitflex Team
          """
        },
        'transferred_to_heirs': {
            'title': 'Funds were transferred',
            'body': """
Hello! 

In accordance with the Lost Key contract created on С-block platform by {owner_address}, 
Funds have been transferred to your address: "{receiver_address}": {link_tx}
If you have any questions, please contact c-support@bitflex.app.

Best wishes, Bitflex Team
            """
        },
    },
    'wedding': {
        'divorce_proposed_from_partner': {
          'title': 'Divorce requested',
          'body': """
Hello! 
          
We would like to inform you that you have requested the divorce with the Partner "{proposer_address}".  
Please wait until your Partner approves or rejects the divorce.
Contract will be executed if no confirmation during the next {days} days. 
If you have any questions please contact c-support@bitflex.app.

Best wishes, Bitflex Team
          """
        },
        'divorce_proposed_to_partner': {
            'title': 'Divorce requested',
            'body': """
Hello! 

We would like to inform you that your Partner "{proposer_address}"  has requested a divorce. 
To approve or reject the divorce please visit  app.c-block.io/my-contracts . 
Contract will be executed if no confirmation during the next {days} days. 
If you approve the divorce, the funds will be divided equally between you and your partner. 
If you reject or ignore the divorce, the funds will be divided in accordance with the the initial % settings. 
If you have any questions please contact c-support@bitflex.app.

Best wishes, Bitflex Team
          """
        },
        'divorce_approved': {
          'title': 'Divorce was approved',
          'body': """
Hello! 

We would like to inform you that your Partner "{executor_address}" has approved the divorce.
The funds were divided equally and sent to both addresses. 

If you have any questions please contact c-support@bitflex.app.

Best wishes, Bitflex Team
          """
        },
        'divorce_rejected': {
          'title': 'Divorce was rejected',
          'body': """
Hello! 

We would like to inform you that your Partner "{executor_address}" has rejected the divorce.
The funds were divided in accordance with initial % settings and sent to both addresses. 
If you have any questions please contact c-support@bitflex.app.

Best wishes, Bitflex Team
          """
        },
        'withdrawal_proposed': {
          'title': 'Funds withdrawal was requested',
          'body': """
Hello! 

We would like to inform you that your Partner "{proposer_address}" has requested a withdrawal of {amount} {token_address}.
To approve or reject the withdrwal please visit  app.c-block.io/my-contracts . 
Contract will be executed if no confirmation during the next {days} days. 
If you have any questions please contact c-support@bitflex.app.

Best wishes, Bitflex Team
          """
        },
        'withdrawal_approved': {
          'title': 'Funds withdrawal was approved',
          'body': """
Hello! 

We would like to inform you that your Partner "{executor_address}" has approved the withdrawal of {amount} {token_address}.
The funds were transferred to your address. 
If you have any questions please contact c-support@bitflex.app.

Best wishes, Bitflex Team
          """
        },
        'withdrawal_rejected': {
          'title': 'Funds withdrawal was rejected',
          'body': """
Hello! 

We would like to inform you that your Partner "{executor_address}" has rejected the withdrawal of {amount} {token_address}.
If you have any questions please contact c-support@bitflex.app.

Best wishes, Bitflex Team
          """
        },
    },


}