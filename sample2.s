        .data
var:  .word   5
        .text
main:
    la $8, var
    lw $9, 0($8)
    addu $2, $0, $9
    jal sum # 4번째
    j exit

sum: sltiu $1, $2, 1
    bne $1, $0, sum_exit
    addu $3, $3, $2 # 7, 12, 17, ...번째. 깎여가는 2를 더하는거니까 종료 전 $3 = 5+4+3+2+1 = 0xf가 됨
    addiu $2, $2, -1
    # addiu $10, $10, -16 # loop 횟수만큼 0x10 증가
    j sum
sum_exit:
    addu $4, $3, $0
    jr $31
exit:
