#ifndef _BUILDFROMCODE_H
#define _BUILDFROMCODE_H

#include <cstring>
#include <cstdint>
#include <stdexcept>
#include <algorithm>
#include <exception>
#include "FastStack.h"
#include "pyc_numeric.h"
#include "bytecode.h"

//#define BLOCK_DEBUG

class UnsupportedOpcodeException : public std::exception
{
	const char* what() const throw ()
	{
		return "Error: Unsupported Opcode";
	}
};

typedef struct Instruction
{
	Instruction(int new_opcode, int new_operand, int new_curpos, int new_pos) : 
		opcode(new_opcode), operand(new_operand), curpos(new_curpos), pos(new_pos) {}
	int opcode = 0;
	int operand = 0;
	int curpos = 0;
	int pos = 0;
} Instruction;

class BuildFromCode
{
public:
	typedef std::vector<Pyc::Opcode> OpSeq;

	BuildFromCode(PycRef<PycCode> param_code, PycModule* param_mod);
	virtual ~BuildFromCode();
	virtual PycRef<ASTNode> build();
	bool getCleanBuild() const;
private:
	void bc_set(size_t new_bc_i);
	void bc_next();
	void bc_update();
	void append_to_chain_store(const PycRef<ASTNode>& chainStore, PycRef<ASTNode> item);
	PycRef<ASTNode> StackPopTop();
	void checkIfExpr();
	void binary_or_inplace();
	void exceptionsChecker();
	void checker();
	void switchOpcode();
	void end_finally();
	void convert_try_finally_to_try_except();
	void add_try_finally_block(int start, bool inited);
	void add_try_block(int end);
	void add_finally_block();
	void add_finally_no_op_block(int end);
	void add_except_block(int elseStart);
	void add_else_block(int end);
	void pop_try();
	void pop_except();
	void pop_try_except_or_try_finally_block();

	// bytecode manipulations (BcMp) functions
	bool isOpSeqMatch(OpSeq opcodeSequence, size_t firstSkipOpcodesNum = 0, bool onlyFirstMatch = false);
	int getOpSeqMatchIndex(OpSeq opcodeSequence, size_t firstSkipOpcodesNum = 0, bool onlyFirstMatch = false);
	bool skipOpSeqIfExists(OpSeq opcodeSequence, size_t firstSkipOpcodesNum = 0);
	bool skipCopyPopExceptReraiseIfExists(size_t firstSkipOpcodesNum);
	bool isOpcodeReturnAfterN(size_t n);

	PycRef<PycCode> code;
	PycModule* mod;
	PycBuffer source;
	FastStack stack;
	stackhist_t stack_hist;
	std::stack<PycRef<ASTBlock> > blocks;
	PycRef<ASTBlock> defblock;
	PycRef<ASTBlock> curblock;

	int opcode;
	int operand;
	int curpos;
	int pos;
	std::vector<Instruction> bc;
	size_t bc_size;
	size_t bc_i;
	// guard class for "peeking" the next instruction(s)
	class BcPeeker
	{
	public:
		BcPeeker(BuildFromCode& buildFromCode, size_t initial_peeks = 0) :
			m_buildFromCode(buildFromCode)
		{
			m_original_bc_i = m_buildFromCode.bc_i;
			this->peekN(initial_peeks);
		}
		~BcPeeker()
		{
			m_buildFromCode.bc_i = m_original_bc_i;
			m_buildFromCode.bc_update();
		}
		void peekOne()
		{
			m_buildFromCode.bc_next();
		}
		void peekN(size_t n)
		{
			while (n > 0)
			{
				this->peekOne();
				n--;
			}
		}
	private:
		size_t m_original_bc_i;
		BuildFromCode& m_buildFromCode;
	};

	int unpack;
	bool else_pop;
	bool variable_annotations;

	/* Use this to determine if an error occurred (and therefore, if we should
	* avoid cleaning the output tree) */
	bool cleanBuild;

	int comprehension_counter;
	std::stack<ExceptTableEntry> exceptTableStack;
	bool previous_depth;
	std::stack<bool> previous_depth_stackhist;
};

#endif