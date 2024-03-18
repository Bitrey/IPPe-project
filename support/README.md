# Project support for IPPe project (parser.py and taci.py)
* Author: Zbyněk Křivka, krivka@fit.vutbr.cz
* Version: 2021-04-21
  
The archive contains several examples in IPPeCode and in its XML representation.

Used directories are only for example and they can be different or no one in other setups. 


## Contained directories/folders
 * `task1` - source code files (with .ippecode extension) serve as the input to parser.py, the reference outputs and reference return codes are in corresponding XML files and RC files
 * `task2` - files with XML representation of IPPeCode (.xml) and the inputs (.in) for READ instructions of taci.py including the reference output (.out) and return codes (.rc)

  
## Bash commands to test the examples at server Merlin (merlin.fit.vutbr.cz):

Manual execution of an example using `parser.py`: 
```bash
cd ~/ippe/task1 # assuming that you have ippe folder with the scripts and tests in your home folder at Merlin
python3.8 parser.py ex1.ippecode ex1-my_output.xml
echo $? > ex1-my_return_code.rc 
```
Then, we need to compare the return codes from the reference `ex1.rc` a generated `ex1-my_return_code.rc`. If there are some differences, the `diff` tool will tell us:
```bash
diff ex1.rc ex1-my_return_code.rc
echo $?  # print the return code of the previously executed command        
```

If there is a match, we get return code zero and we can compare the XML files. You can use JExamXML utility (available at Merlin) to do that in clever way:
```bash
java -jar /pub/courses/ipp/jexamxml/jexamxml.jar ex1.xml ex1-my_output.xml diffs.xml  /D /pub/courses/ipp/jexamxml/options
echo "Return code is $?"  # non-zero return code means that XML files differ and then diffs.xml contains some details about the difference
```

Manual execution of an example using `taci.py`: 
```bash
cd ~/ippe/task2 # assuming that you have ippe folder with the scripts and tests in your home folder at Merlin
python3.8 taci.py ex1.xml < ex1.in > ex1.your_out
echo $? > ex1-my_return_code.rc 
```

Again, we use `diff` to check that reference and generated return code are the same:
```bash
diff ex1.rc ex1-my_return_code.rc
echo $?  # print the return code of the previously executed command, zero means that both rc are same       
```

Now, if the return codes are the same and zero, we use `diff` to check the reference and the generated output files (for non-zero return codes, we just check the return codes and error message in the standard error output):
```bash
diff ex1.out ex1-my_output.out
echo $?  # print the return code of the previously executed command, zero means that both rc are same
```
