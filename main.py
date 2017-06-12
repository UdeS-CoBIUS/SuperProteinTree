from ete3 import Tree
from ete3 import Tree
from copy import deepcopy, copy

def buildTree(file):
    clusters = []
    f = open(file)
    lines = f.readlines()
    for l in lines:
        c = l.split(" ")[0].replace("\n", "")
        c = c.replace(")", "", 1000).replace("(", "", 1000)
        elts = c.split("-")
        clusters.append(elts)
    toremove = []
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            set1 = set(clusters[i])
            set2 = set(clusters[j])
            if set1.issubset(set2):
                toremove.append(i)
            if set2.issubset(set1):
                toremove.append(j)

    toremove = list(set(toremove))
    toremove.sort()

    for i in range(len(toremove) - 1, -1, -1):
        clusters.remove(clusters[toremove[i]])
    size = [0] * 7

    for c in clusters:
        size[len(c) - 1] += 1
    print size
    return clusters

def tree_reduction_from_cluster(leafSetToSave, tree):
    leafSetToBeReduced = [p for p in tree.get_leaf_names() if p not in leafSetToSave]
    proteinsNotRemoved = []
    for protein in leafSetToBeReduced:
        matches = tree.search_nodes(name=protein)
        if len(matches) == 1:
            proteinRemain = matches[0]
            proteinRemain.delete()
        else:
            proteinsNotRemoved.append(protein)
    return tree, proteinsNotRemoved

def span(proteinLeafSet, proteinTreeSet):
    """
    this function compute span for a given proteinIdAtLeaf set associated to a set of trees
    :param proteinLeafSet: proteinIdAtLeaf set as a string ["a01", "a02", "b10"]
    :param proteinTreeSet: a python dict which has protein name as key and tree as value asscociated to each key
    :return: dict which represent a span partition for each proteinIdAtLeaf {"a01" : [p1,p2], "a02" : [p3], "b10" : [p3]}
    """
    spanSet = {}
    for proteinIdAtLeaf in proteinLeafSet:
        for treeId, tree in proteinTreeSet.iteritems():
            if proteinIdAtLeaf in tree.get_leaf_names():
                if proteinIdAtLeaf in spanSet.keys():
                    spanSet[proteinIdAtLeaf].append(treeId)
                else:
                    spanSet[proteinIdAtLeaf] = [treeId]
    return spanSet

def p_span(spanSet):
    """
    this function compute the span partition from the spanSet
    :param spanSet: {"a01" : [p1,p2], "a02" : [p3], "b10" : [p3]}
    :return: spanPartition {"S1": ["a01"], "S2": ["a02", "b10"]}
    """
    keys = spanSet.keys()
    spanPartition = {}
    useKeys = []
    i = 1
    for key1 in keys:
        if key1 in useKeys:
            continue
        else:
            spanPartition["S" + str(i)] = [key1]
            treeOfTree1 = spanSet[key1]
            useKeys.append(key1)
            for key2 in keys:
                if key2 in useKeys:
                    pass
                else:
                    if set(spanSet[key2]) == set(treeOfTree1):
                        spanPartition["S" + str(i)].append(key2)
                        useKeys.append(key2)
            i = i + 1
    return spanPartition

def span_extend(spanPartition, proteinTreeSet):
    """
    this function is an extention of span function to the span Partition set
    :param spanPartition: {"S1": ["a01"], "S2": ["a02", "b10"]}
    :param proteinTreeSet: {"p1": tree1, "p2": tree2, ..., "pk": treek}
    :return: spanSetExtend : {"S1": [p1, p2], "S2": [p3]}
    """
    spanSetExtend = {}
    spanIds = spanPartition.keys()
    for spanId in spanIds:
        spanSetExtend[spanId] = []
        for proteinId in spanPartition[spanId]:
            for treeId, tree in proteinTreeSet.iteritems():
                if proteinId in tree.get_leaf_names():
                    if not(treeId in spanSetExtend[spanId]):
                        spanSetExtend[spanId].append(treeId)
    return spanSetExtend

def tree_reduction(leafSetToBeReduced, tree):
    proteinsNotRemoved = []
    c = 0
    l = len(tree.get_leaf_names())
    for protein in leafSetToBeReduced:
        matches = tree.search_nodes(name=protein)
        if len(matches) == 1:
            c = c +1
            proteinRemain = matches[0]
            proteinRemain.delete()
        else:
            #exit()
            proteinsNotRemoved.append(protein)
    if c == l :
        return None, proteinsNotRemoved
    else:
        tree = makeBinaryCall(copy(tree))
        return tree, proteinsNotRemoved

def su_tree(spanPartition,proteinTreeSet):
    """
    this function compute/extract subtree from P.
    :param spanPartition: {'S3': ['b01'], 'S2': ['a31', 'c21', 'b31', 'd31', 'c31'], 'S1': ['a21', 'b21', 'b11', 'c12'], 'S5': ['c11'], 'S4': ['b02']}
    :param proteinTreeSet: {"p1": t1, "p2": t2, "p3":t3}
    :return: tree for each Si {'S3': t3, 'S2': t2, 'S1': t1, 'S5': t5, 'S4': t4}
    """
    #print spanPartition
    #print proteinTreeSet
    spanTree = {}
    for spandId, listProteinId in spanPartition.iteritems():
        #print spandId, listProteinId
        if len(listProteinId) == 1:
            spanTree[spandId] =  Tree("(" + listProteinId[0] + ");")
            #print "1"
            #print spanTree[spandId]
        else:
            idOfSubProteinTree = proteinTreeSet.keys()
            for idTree in idOfSubProteinTree:
                tmpProteinTree =  deepcopy(proteinTreeSet[idTree])
                #print tmpProteinTree
                listProteinIdOfTree = tmpProteinTree.get_leaf_names()
                if set(listProteinId).issubset(set(listProteinIdOfTree)):
                    proteinIdToRemoved = list(set(listProteinIdOfTree) - set(listProteinId))
                    for protein in proteinIdToRemoved:
                        matches = tmpProteinTree.search_nodes(name=protein)
                        if len(matches) == 1:
                            proteinRemain = matches[0]
                            proteinRemain.delete()
                        else:
                            print "ERROR: can't delete proteinId"
                            exit(-1)
                    if not(spandId in spanTree.keys()):
                        spanTree[spandId] = tmpProteinTree
                    else:
                        t1 = deepcopy(spanTree[spandId])
                        t2 = deepcopy(tmpProteinTree)
                        t11 = makeBinaryCall(t1)
                        t22 = makeBinaryCall(t2)
                        rf, max_rf, common_leaves, parts_t1, parts_t2, v6, v7 = t11.robinson_foulds(t22)
                        if rf != 0:
                            print "there trees which didn't have the same topologie \n 1- ", spanTree[spandId].write(), "\n2- ",   tmpProteinTree.write()
                else:
                    continue
    return spanTree
def findNode(leaves, tree):

    c = 0
    for l in leaves:
        m = tree.search_nodes(name=l)
        if len(m) > 0:
            c = c + 1

    if c == len(tree.get_leaf_names()):
        return tree

    if len(leaves) > 1:
        ancestor = tree.get_common_ancestor(leaves)
    elif len(leaves) == 1:
        ancestor = tree.search_nodes(name=leaves[0])[0]
    return ancestor

def makeBinaryOld(tree):
    while len(tree.get_children()) == 1:
        tree = tree.get_children()[0]

    for node in tree.traverse("preorder"):
        if node.is_leaf:
            pass        
        else:
            if len(node.get_children()) == 2:
                continue
            elif len(node.get_children()) == 1:
                child = node.get_children()[0]
                child2 = deepcopy(child)
                child.delete()
                parent = node.up
                parent.add_child(child2)
                node.delete()
            else:
                return False
    return tree
def deleteNoName(tree):
    matches = tree.search_nodes(name="NoName")

    for node in matches:
        node.delete()
    return  tree
def checkTree(tree):

    for node in tree.traverse("preorder"):
        l = len(node.get_children())
        if l!=2 and l !=0:
            return False
    return True

def makeBinaryCall(tree1):
    tree1, flag = makeBinary(deepcopy(tree1))
    while flag:
        tree1, flag = makeBinary(deepcopy(tree1))
    return  tree1

def makeBinary(tree):
    while len(tree.get_children()) == 1:
        tree = deepcopy(tree.get_children()[0])

    for node in tree.traverse("preorder"):
        l = len(node.get_children())
        if l == 0:

            pass
        else:

            if l == 2:
                continue
            elif l == 1:
                c = deepcopy(node.get_children()[0])
                parent = node.up
                parent.add_child(c)
                node.detach()

                return tree, True
            elif l == 4:
                node.get_children()[1].detach()
                node.get_children()[0].detach()
                return tree, True

    return tree, False

def getUandV(Q, spanSetExtend, proteinTreeSet, spanTree):
    """
    choose Su and Sv such that Su ^ Sv is a creation node
    :param Q: {'S2': ['a31', 'c21', 'b31', 'd31', 'c31'], 'S1': ['a21', 'b21', 'b11', 'c12'], 'S5': ['c11'], 'S34': ['b01', 'b02']}
    :param spanSetExtend: {'S3': ['p1'], 'S2': ['p2', 'p3', 'p1'], 'S1': ['p3'], 'S5': ['p2', 'p1'], 'S4': ['p2']}
    :param proteinTreeSet: {"p1": t1, "p2": t2, "p3":t3}
    :param spanTree: {'S3': t3, 'S2': t2, 'S1': t1, 'S5': t5, 'S4': t4}
    :return:
    """
    keys = Q.keys()
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            Su = keys[i]
            Sv = keys[j]

            spanSetExtendSu = spanSetExtend[Su]
            spanSetExtendSv = spanSetExtend[Sv]
            intersection = [val for val in spanSetExtend[Su] if val in spanSetExtend[Sv]]
            if len(intersection) == 0:

                treesOfSu = spanSetExtend[Su]
                treesOfSv = spanSetExtend[Sv]
                setTreeU = []
                setTreeV = []
                for tree in treesOfSu:
                    treeUReduced = None
                    if set(Q[Su]) != set(proteinTreeSet[tree].get_leaf_names()):
                        treeUReduced, proteinsNotRemoved = tree_reduction(deepcopy(Q[Su]), deepcopy(proteinTreeSet[tree]))
                        try:
                            if treeUReduced != None and treeUReduced.get_leaf_names() != ['']:
                                setTreeU.append(treeUReduced.write())
                        except:
                            print treeUReduced
                            print "Oops!"

                for tree in treesOfSv:
                    treeVReduced = None

                    if set(Q[Sv]) != set(proteinTreeSet[tree].get_leaf_names()):
                        treeVReduced, proteinsNotRemoved = tree_reduction(deepcopy(Q[Sv]), deepcopy(proteinTreeSet[tree]))

                        try:
                            if treeVReduced != None and treeVReduced.get_leaf_names() != ['']:
                                setTreeV.append(treeVReduced.write())
                        except:
                            print treeVReduced
                            print "Oops"

                if set(setTreeU) == set(setTreeV):
                    newNode = Tree(";")
                    newNode.add_child(spanTree[Su])
                    newNode.add_child(spanTree[Sv])

                    print "creat"
                    spanSetExtendSuList = deepcopy(spanSetExtendSu)
                    spanSetExtendSvList = deepcopy(spanSetExtendSv)
                    for St in Q.keys():
                        spanSetExtend[St] = [p for p in spanSetExtend[St] if p not in spanSetExtendSv]
                    return Su, Sv, newNode, spanSetExtendSuList, spanSetExtendSvList
    return None, None, None, None, None

def checkCompability(tree2, proteinTreeList):
    """ UTILISER DEEPCOPY POUR EVITER MODIFICATION DES ARBRES LORS DE LA FONCTION!!!!
    :param tree1: tree1
    :param proteinTreeList [t1, t2, ....,  tk]
    """
    flag = True
    leafOfTree1 = tree2.get_leaf_names()
    for tr in proteinTreeList:
        tree1 = deepcopy(tree2)
        t = deepcopy(tr)

        leafOfT = t.get_leaf_names()
        intersctionLeaf = [p for p in leafOfTree1 if p in leafOfT]

        toRemoveInTree1 = [x for x in leafOfTree1 if x not in intersctionLeaf]
        toRemoveInTree2 = [x for x in leafOfT if x not in intersctionLeaf]
        for protein in toRemoveInTree1:
            matches = tree1.search_nodes(name=protein)
            if len(matches) == 1:
                proteinToremove = matches[0]
                proteinToremove.delete()

        for protein in toRemoveInTree2:
            matches = t.search_nodes(name=protein)
            if len(matches) == 1:
                proteinToremove = matches[0]
                proteinToremove.delete()

        tree1 = makeBinaryCall(tree1)
        t = makeBinaryCall(t)
        arbre1 = tree1.write(format=9)
        arbre2 = t.write(format=9)
        arbre1 = arbre1.replace("NoName,", "", 1000).replace("(,", "(", 1000)
        arbre2 = arbre2.replace("NoName,", "", 1000).replace("(,", "(", 1000)
        tree1 = Tree(arbre1)
        t = Tree(arbre2)


        tree1 = makeBinaryCall(tree1)
        t = makeBinaryCall(t)

        arbre1 = tree1.write(format=9).replace("NoName,", "", 1000)
        arbre2 = t.write(format=9).replace("NoName,", "", 1000)
        t1 = Tree(arbre1)
        t2 = Tree(arbre2)
        rf, max_rf, common_leaves, parts_t1, parts_t2, v6, v7 = t1.robinson_foulds(t2)
        if rf != 0:
            flag = False
            break

    if flag == False:
        return False
    else:
        return True

def getUandVNotCreationEvent(Q, spanSetExtend, proteinTreeSet, spanTree, newNodesListe):
    print "not creat"
    """
    this function choose Su and Sv such that P|su was build at a previous iteration of step 3
    :param Q: {'S2': ['a31', 'c21', 'b31', 'd31', 'c31'], 'S1': ['a21', 'b21', 'b11', 'c12'], 'S5': ['c11'], 'S34': ['b01','b02']}
    :param spanSetExtend: {'S3': ['p1'], 'S2': ['p2', 'p3', 'p1'], 'S1': ['p3'], 'S5': ['p2', 'p1'], 'S4': ['p2'], 'S34' : [p1, p2]}
    :param proteinTreeSet: {"p1": t1, "p2": t2, "p3":t3}
    :param spanTree: {'S3': t3, 'S2': t2, 'S1': t1, 'S5': t5, 'S4': t4}
    :param newNodesListe: ['Sij', 'Sik']
    :return:
    """
    resultSu = None
    resultSv = None
    resultTree = None
    Su = newNodesListe[0]
    newNodesListe.pop(0)
    keysOfQ = Q.keys()

    for key in keysOfQ:

        setSu = deepcopy(set(spanSetExtend[Su]))
        setSv = deepcopy(set(spanSetExtend[key]))
        if key != Su :
            Sv = key
            Tu = spanTree[Su]
            Tv = spanTree[Sv]
            Tu = makeBinaryCall(Tu)
            Tv = makeBinaryCall(Tv)
            P_primeNode = Tree(";")
            P_primeNode.add_child(Tu)
            P_primeNode.add_child(Tv)
            TreeOfSv = [proteinTreeSet[x] for x in spanSetExtend[Sv]]
            compability = checkCompability(deepcopy(P_primeNode), deepcopy(TreeOfSv))

            if compability == True:
                if setSu == setSv:
                    return Su, Sv, P_primeNode
                else:
                    resultSu, resultSv, resultTree = deepcopy(Su), deepcopy(Sv), deepcopy(P_primeNode)
            else:
                side = 0
                while side <= 1:

                    if side == 1:
                        tmp = deepcopy(Su)
                        Su = deepcopy(Sv)
                        Sv = deepcopy(tmp)
                    side += 1
                    Tu = spanTree[Su]
                    Tv = spanTree[Sv]
                    Tu = makeBinaryCall(Tu)
                    Tv = makeBinaryCall(Tv)

                    for nodeF in Tv.traverse("preorder"):
                        tree = deepcopy(Tv)
                        if len(nodeF.get_children())>1:
                            leaves = nodeF.get_leaf_names()
                            node = findNode(leaves, tree)

                            leafChild = Tree(node.get_children()[0].write()) 
                            rightChild = Tree(node.get_children()[1].write())
                            nodeInsert = Tree(";")
                            nodeInsert.add_child(Tu)
                            nodeInsert.add_child(leafChild)
                            node.get_children()[0].detach()
                            node.add_child(nodeInsert)
                            tree = makeBinaryCall(tree)

                            compability = checkCompability(deepcopy(tree), deepcopy(TreeOfSv))
                            if compability == True:
                                return Su, Sv, tree
                            else:
                                tree = deepcopy(Tv)
                                leaves = nodeF.get_leaf_names()
                                node = findNode(leaves, tree)
                                leafChild = Tree(node.get_children()[0].write())
                                rightChild = Tree(node.get_children()[1].write())

                                nodeInsert = Tree(";")
                                nodeInsert.add_child(Tu)
                                nodeInsert.add_child(rightChild)
                                node.get_children()[1].detach()
                                node.add_child(nodeInsert)
                                tree = makeBinaryCall(tree)

                                compability = checkCompability(deepcopy(tree), deepcopy(TreeOfSv))
   
                                if compability == True:
                                    if setSu == setSv:
                                        return Su, Sv, tree
                                    else:
   
                                        resultSu, resultSv, resultTree = deepcopy(Su), deepcopy(Sv), deepcopy(tree)
   
    if resultSu == None:
        return None, None, None
    else:
        return resultSu, resultSv, resultTree

def algorithm2(Q, spanTree, proteinTreeSet, spanSetExtend, proteinLeafSet):
    """
    this is the implementation of algorithm 2
    :param spanPartition / Q: {'S3': ['b01'], 'S2': ['a31', 'c21', 'b31', 'd31', 'c31'], 'S1': ['a21', 'b21', 'b11', 'c12'], 'S5': ['c11'], 'S4': ['b02']}
    :param spanTree: {'S3': t3, 'S2': t2, 'S1': t1, 'S5': t5, 'S4': t4}
    :param proteinTreeSet : {"p1": t1, "p2": t2, "p3":t3}
    :param spanSetExtend : ==>  {'S3': ['p1'], 'S2': ['p2', 'p3', 'p1'], 'S1': ['p3'], 'S5': ['p2', 'p1'], 'S4': ['p2']}
    :return: protein Tree P
    """
    proteinTreeSetCopy = deepcopy(proteinTreeSet)
    newNodesListe = []
    creationTrees = []
    i = 999999
    while len(Q.keys()) > 1:
        print "begin whil Q", len(Q.keys()), len(proteinTreeSet.keys())
   
        i = i +1
        Su, Sv, newNode, spanSetExtendSu, spanSetExtendSv = getUandV(Q, spanSetExtend, proteinTreeSet, spanTree)
        if Su == None:
            Su, Sv, newNode = getUandVNotCreationEvent(Q, spanSetExtend, proteinTreeSet, spanTree, newNodesListe)
        else:
            creationTrees.append(deepcopy(newNode))
   
        if Su != None:
            Sw = "S" + str(i) + "-" + Su[1:] + "-" + Sv[1:]
            Pw = "p" + str(i) + "-" + Su[1:] + "-" + Sv[1:]
            if (len(spanTree["S"+  Su[1:]].get_leaf_names()) + len(spanTree["S"+  Sv[1:]].get_leaf_names()) != len(newNode.get_leaf_names())) or len(spanTree["S"+  Su[1:]].get_leaf_names()) >= len(newNode.get_leaf_names()) or len(spanTree["S"+  Sv[1:]].get_leaf_names()) >= len(newNode.get_leaf_names()):
                print Su, Sv, Q[Su], Q[Sv], spanSetExtend[Su], spanSetExtend[Sv]
                print "ERROOR"
                exit()
            Q[Sw] = list(set(Q[Su] + Q[Sv]))
            ListSu = deepcopy(list(set(Q[Sv])))
            Q.pop(Su)
            Q.pop(Sv)
            spanTree[Sw] = newNode
            spanExtendOfSw = span_extend({Sw : ListSu}, proteinTreeSetCopy)
            spanSetExtend[Sw] = spanExtendOfSw[spanExtendOfSw.keys()[0]]
            newNodesListe = [Sw]
            proteinTreeSet[Pw] = deepcopy(newNode)
        else:
            l = []
            for key in Q.keys():
   
                for e in spanTree[key].get_leaf_names():
                    l.append(e)
   
            print set(proteinLeafSet) - set(l)

            for key in Q.keys():
                print spanTree[key]
                tree =  makeBinaryCall(spanTree[key])
                print tree.write(format=9)
            print "\n\n\n\n\n\nNO SOLUTION DUE TO THE INCOMPATIBILITY OF TREES\n\n\n\n\n\n"
            for tree in creationTrees:
                # print "maximun creation-free " + str(i)
                print tree.write(format=9)
            exit()
    return creationTrees

def main():

    tree = Tree('((((((ENST00000378295,(ENST00000346387,ENST00000604479)),(ENST00000354437,(ENST00000604074,(ENST00000603362,ENST00000357733)))),((ENST00000378290,ENST00000378288),(ENST00000378285,ENST00000378280))),ENSBTAT00000007643),(ENSMUST00000105644,(ENSMUST00000105643,(ENSMUST00000097762,ENSMUST00000133533)))),((ENSGALT00000011850,ENSGALT00000033346),((ENSMUST00000065523,((ENSMUST00000115310,(ENSMUST00000115305,(ENSMUST00000115307,ENSMUST00000115308))),(ENSMUST00000115304,(ENSMUST00000040231,ENSMUST00000115306)))),(ENSBTAT00000020544,(ENST00000264731,((ENST00000354600,(ENST00000449992,(ENST00000456148,ENST00000392463))),(ENST00000440651,(ENST00000392460,((ENST00000418709,ENST00000437221),(ENST00000392461,ENST00000320472))))))))));')
    clusters = buildTree("/home/local/USHERBROOKE/kuie2201/NetBeansProjects/OrthoMCL/Datas/TP53_restrict_86/clusters_all.cls")
    proteinTreeSet = {}
    i = 1
    for c in clusters:

        treeP, notRemove = tree_reduction_from_cluster(c, deepcopy(tree))
        treeP = makeBinaryCall(deepcopy(treeP))
        if not(checkTree(treeP)):
            treeP = makeBinaryCall(deepcopy(treeP))

            if not(checkTree(treeP)):
                exit("IMPOSSIBLE TO MAKE SUB TREES")
        else:
            pass

        p = "p" + str(i)
        proteinTreeSet[p] = treeP
        i = i + 1
    proteinLeafSet = tree.get_leaf_names()

    spanSet = span(deepcopy(proteinLeafSet), deepcopy(proteinTreeSet))
    spanPartition = p_span(deepcopy(spanSet))
    spanSetExtend = span_extend(deepcopy(spanPartition), deepcopy(proteinTreeSet))

    spanTree = su_tree(deepcopy(spanPartition), deepcopy(proteinTreeSet))
    Q = spanPartition

    liste = []
    for p in spanPartition.keys():
        for e in spanPartition[p]:
            liste.append(e)
    print len(list(set(liste)))
    print set(tree.get_leaf_names()) - set(liste)

    creationTrees = algorithm2(Q, spanTree, proteinTreeSet, spanSetExtend, proteinLeafSet)
    if len(Q.keys()) == 1:
        print "\n\n SOLUTION : \t \t ",  "\n\n\n\n",  len(spanTree[Q.keys()[0]].get_leaf_names()), spanTree[Q.keys()[0]]
        print spanTree[Q.keys()[0]].write(format=9)
        i = 1
        for tree in creationTrees:

            print tree.write(format = 9)

            i = i +1
    else:
        print "PAS POSSIBLE DE CONSTRUIRE P", "\n Q :", Q, "\n spanTree : ", spanTree, "\n proteinTreeSet :", proteinTreeSet, "\n spanSetExtend : ", spanSetExtend
if __name__ == "__main__":
    main()
   
