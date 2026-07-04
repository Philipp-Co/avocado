
#
# ---------------------------------------------------------------------------------------------------------------------
#
from typing import List, Self, Optional
from dataclasses import dataclass
from .generate_codes import generate_huffman_codes, build_huffman_tree

#
# ---------------------------------------------------------------------------------------------------------------------
#
@dataclass
class Token:
    data: str
    pass
#
# ---------------------------------------------------------------------------------------------------------------------
#


@dataclass
class Node:
    
    symbol: Optional[str] = None
    frequency: Optional[float] = None
    left: Optional[Node] = None
    right: Optional[Node] = None

    pass
#
# ---------------------------------------------------------------------------------------------------------------------
#

class HuffmanTreeIterator:

    def __init__(self, node: Node):
        self.__node: Node = node
        pass

    def symbol(self) -> str:
        if self.__node is None or self.__node.symbol is None:
            raise AssertionError('Symbol not found yet.')
        return self.__node.symbol

    def next_bit(self, bit: bool) -> bool:
        if self.__node is None:
            raise AssertionError('Node is None. You are asking for a Code that does not exist.')
        if self.__node.symbol is not None:
            raise AssertionError
        if bit:
            self.__node = self.__node.right
        else:
            self.__node = self.__node.left
        return self.__node is not None and self.__node.symbol is not None

    pass
#
# ---------------------------------------------------------------------------------------------------------------------
#

class Tree:

    def __init__(self, codes: Dict[str, str]):

        self.__root_node = Node()

        self.__construct(
            codes
        )
        pass

    def __in_order_traversal(self, node: Node, code: str, output: Dict[str, str]):
        if node.left is not None:
            self.__in_order_traversal(node.left, code + '0', output)
        if node.right is not None:
            self.__in_order_traversal(node.right, code + '1', output)
        if node.left is None and node.right is None:
            output[node.symbol] = code
        pass

    def codes(self) -> Dict[str, str]:
        output = {}
        self.__in_order_traversal(self.__root_node, '', output)
        return output

    def __construct(self, codes: Dict[str, str]) -> None:
        for symbol in codes:
            self.__insert_code(
                symbol, codes[symbol], self.__root_node, 
            )
        pass

    def __insert_code(self, symbol: str, code: str, node: Node) -> None:
        if len(code) == 0:
            node.symbol = symbol
        else:
            if code[0] == '0':
                if node.left is None:
                    node.left = Node()
                self.__insert_code(symbol, code[1:], node.left)
            else:
                if node.right is None:
                    node.right = Node()
                self.__insert_code(symbol, code[1:], node.right)
        pass

    def iterator(self) -> HuffmanTreeIterator:
        return HuffmanTreeIterator(self.__root_node)

    pass


#
# ---------------------------------------------------------------------------------------------------------------------
#

class TreeBuilder:
    
    @staticmethod
    def from_dict(codes: Dict[str, str]) -> Tree:
        return Tree(
            codes
        )
    
    @staticmethod
    def from_str(data: str) -> Tree:
        return TreeBuilder.from_dict(
            generate_huffman_codes(
                build_huffman_tree(
                    data
                )
            )
        ) 

    pass

#
# ---------------------------------------------------------------------------------------------------------------------
#

