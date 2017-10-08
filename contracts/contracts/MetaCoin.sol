pragma solidity 0.4.15;


contract MetaCoin {

  //set variables
  address public buyer;
  address public seller;
  //uint public initial_nav;

  //constructor runs once
  function MetaCoin(address _seller) {
    buyer = msg.sender;
    seller = _seller;
  }

  //make payment to seller
  function payoutToSeller() payable returns(bool success) {
    if(msg.sender == buyer) {
    seller.send(1e18);
	return true;
    }
  }

  //refund transaction
  function refundToBuyer() payable returns(bool success) {
    if(msg.sender == seller) {
    buyer.send(this.balance);
	return true;
    }
  }

  //query for balance
  function getBalance() constant returns (uint) {
    return this.balance;
  }

}
 
