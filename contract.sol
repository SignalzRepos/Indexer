contract StoreVar {
    uint8 public _myVar;

    event someEvent(uint indexed _var);

    function setVar(uint8 _var) public {
        _myVar = _var;
        emit someEvent(_var);
    }

    function getVar() public view returns (uint8) {
        return _myVar;
    }
}