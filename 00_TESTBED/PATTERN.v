
`ifdef DRAM_PAT1
    `define DRAM_PAT "../00_TESTBED/DRAM/dram1.dat"
`elsif DRAM_PAT2
    `define DRAM_PAT "../00_TESTBED/DRAM/dram2.dat"
`elsif DRAM_PAT3
    `define DRAM_PAT "../00_TESTBED/DRAM/dram0.dat"
`else
    `define DRAM_PAT "../00_TESTBED/DRAM/dram2.dat"
`endif

`ifdef RTL
    `define CYCLE_TIME 10.0
`elsif GATE
    `ifndef CYCLE_TIME
        `define CYCLE_TIME 10.0
    `endif
`else
    `define CYCLE_TIME 10.0
`endif

`include "../00_TESTBED/pseudo_DRAM.v"

module PATTERN(
    // Input Signals
    clk,
    rst_n,
    in_valid,
    in_pic_no,
    in_mode,
    in_ratio_mode,
    out_valid,
    out_data
);

/* Input for design */
output reg        clk, rst_n;
output reg        in_valid;

output reg [3:0] in_pic_no;
output reg  in_mode;
output reg [1:0] in_ratio_mode;

input out_valid;
input [7:0] out_data;

real CYCLE = `CYCLE_TIME;
integer pat_read;
integer PAT_NUM;
integer total_latency, latency;
integer i_pat;
integer pic_num;
integer expo_mode;
integer i, j, k, l, m;
integer action;

integer temp;

parameter DRAM_p_r = `DRAM_PAT;
reg	[7:0]	DRAM_r	[0:196607];
reg [7:0] pic [0:2][0:31][0:31];
reg [7:0] gray_pic [0:31][0:31];
reg [7:0] gray_pic_dx_2 [0:1];  // -
reg [7:0] gray_pic_dx_4 [0:3][0:2]; // -
reg [7:0] gray_pic_dx_6 [0:5][0:4]; // -
reg [7:0] gray_pic_dy_2 [0:1]; // |
reg [7:0] gray_pic_dy_4 [0:2][0:3]; // |
reg [7:0] gray_pic_dy_6 [0:4][0:5]; // |

reg [11:0] sum_pic_constract_2;
reg [10:0] sum_pic_constract_4;
reg [11:0] sum_pic_constract_6;
reg [11:0] max_constract;
reg [1:0] GOLDEN_CONTRAST;

reg [17:0] img_mean [0:2];
reg [20:0] img_mean_temp;
// reg [12:0] img_mean_final;
reg [7:0] GOLDEN_MEAN;
reg overflow;

//////////////////////////////////////////////////////////////////////
// Write your own task here
//////////////////////////////////////////////////////////////////////
initial clk=0;
always #(CYCLE/2.0) clk = ~clk;

initial begin
    PAT_NUM = 400;
    reset_signal_task;
    $readmemh(DRAM_p_r, DRAM_r);
    for (i_pat = 0; i_pat <= PAT_NUM; i_pat = i_pat + 1) begin
        action = $urandom%2;
        if (action==0)
            t_color_auto_focus;
        else
            t_color_auto_exposure;
        total_latency = total_latency + latency;
    end

    $display("*************************************************************************");
    $display("*                         Congratulations!                              ");
    $display("*                Your execution cycles = %5d cycles          ", total_latency);
    $display("*                Your clock period = %.1f ns          ", CYCLE);
    $display("*                Total Latency = %.1f ns          ", total_latency*CYCLE);
    $display("*************************************************************************");
    $finish;
end

task reset_signal_task; begin

    force clk = 0;
    in_valid = 0;
    in_pic_no = 'hx;
    in_mode = 'hx;

    #5 rst_n = 0;
    #(CYCLE*2) rst_n = 1;

    release clk;
    #(100);
    if (out_valid!==0 || out_data!==0)
    begin
        $display("********************************\n");
        $display("You don't successfully reset!\n");
        $display("********************************\n");
        $finish;
    end
    total_latency = 0;

end endtask

task t_initial_signal; begin
    latency = 0;
    in_valid = 0;
    in_pic_no = 'bx;
    in_mode = 'bx;
    in_ratio_mode = 'bx;
end
endtask

task t_calculate_latency; begin
    latency = 0;
    while(out_valid !==1)
    begin
        @(negedge clk);
        latency = latency + 1;
        if (latency > 10000)
        begin
            $display("********************************\n");
            $display("You latency is over %d cycles!\n", latency);
            $display("********************************\n");
            $finish;
        end
    end
end
endtask

task t_color_auto_exposure; begin
    t_initial_signal;
    @(negedge clk);

    pic_num = $urandom%15;
    expo_mode = $urandom%3;

    // $display("t_color_auto_exposure: pic_num=%d, expo_mode=%d", pic_num, expo_mode);

    in_valid = 1;
    in_pic_no = pic_num;
    in_mode = 1;
    in_ratio_mode = expo_mode;

    @(negedge clk);

    for (k = 0; k < 3; k=k+1) begin
        for (i = 0; i < 32; i = i + 1) begin
            for (j = 0; j < 32; j = j + 1) begin
                pic[k][i][j] = DRAM_r[65536+pic_num*3072 + k*1024 + i*32 + j];
            end
        end
    end


    for (k = 0; k < 3; k=k+1) begin
        for (i = 0; i < 32; i = i + 1) begin
            for (j = 0; j < 32; j = j + 1) begin
                case(expo_mode)
                    0: begin
                        pic[k][i][j] = pic[k][i][j]>>2;
                    end
                    1: begin
                        pic[k][i][j] = pic[k][i][j]>>1;
                    end
                    2: begin
                        pic[k][i][j] = pic[k][i][j];
                    end
                    3: begin
                        {overflow, pic[k][i][j]} = pic[k][i][j]*2;
                        if (overflow) begin
                            pic[k][i][j]=255;
                        end
                    end
                endcase
            end
        end
    end

    for (k = 0; k < 3; k=k+1) begin
        for (i = 0; i < 32; i = i + 1) begin
            for (j = 0; j < 32; j = j + 1) begin
                DRAM_r[65536+pic_num*3072 + k*1024 + i*32 + j] = pic[k][i][j];
            end
        end
    end

    // for (j = 0; j < 32; j = j + 1)
    // begin
    //     $display("pic[2][31][%d]: %h", j, pic[2][31][j]);
    // end
    for (k = 0; k < 3; k=k+1) begin
        img_mean[k]= 0;
    end
    for (k = 0; k < 3; k=k+1) begin
        for (i = 0; i < 32; i = i + 1) begin
            for (j = 0; j < 32; j = j + 1) begin
                if (k==0 || k==2) begin
                    img_mean[k] = img_mean[k] + (pic[k][i][j]>>2);
                end
                else begin
                    img_mean[k] = img_mean[k] + (pic[k][i][j]>>1);
                end
            end
        end
    end

    img_mean_temp = (img_mean[0] + img_mean[1] + img_mean[2]);

    GOLDEN_MEAN = img_mean_temp[20:10];
    // $display("GOLDEN_MEAN: %d", GOLDEN_MEAN);

    t_initial_signal;
    t_calculate_latency;
    // @(negedge clk);
    if (GOLDEN_MEAN>out_data)
        temp=GOLDEN_MEAN-out_data;
    else
        temp=out_data-GOLDEN_MEAN;
    // if (GOLDEN_MEAN!==out_data)
    if (temp>2)
    begin
        $display("********************************\n");
        $display("\033[31mWrong Answer for function color auto exposure!\033[0m\n");
        $display("Golden Answer: %d, Your Answer: %d\n", GOLDEN_MEAN, out_data);
        $display("********************************\n");
        @(negedge clk);
        $finish;
    end
    else
    begin
        // $display("Golden Answer: %d, Your Answer: %d\n", GOLDEN_MEAN, out_data);
        $display("\033[32mPass Pattern %d, Function: color auto exposure\033[0m", i_pat);
    end
    @(negedge clk);

end
endtask

task t_color_auto_focus; begin
    t_initial_signal;
    @(negedge clk);
    in_valid = 1;
    pic_num = $urandom%15;
    // $display("pic_num = %d", pic_num);
    // pic_num = 14;


    in_pic_no = pic_num;
    in_mode = 0;
    @(negedge clk);
    
    sum_pic_constract_2 = 0;
    sum_pic_constract_4 = 0;
    sum_pic_constract_6 = 0;

    for (k = 0; k < 3; k=k+1) begin
        for (i = 0; i < 32; i = i + 1) begin
            for (j = 0; j < 32; j = j + 1) begin
                pic[k][i][j] = DRAM_r[65536+pic_num*3072 + k*1024 + i*32 + j];
            end
        end
    end

    for (i = 0; i < 32; i = i + 1) begin
        for (j = 0; j < 32; j = j + 1) begin
            gray_pic[i][j] = (pic[0][i][j]>>2) + (pic[1][i][j]>>1) + (pic[2][i][j]>>2);
            // $display("gray_pic[%d][%d] = %h", i, j, gray_pic[i][j]);
        end
    end
    
    for (i = 0; i < 2; i = i + 1) begin
        gray_pic_dx_2[i] = (gray_pic[i+15][16]>gray_pic[i+15][15])?gray_pic[i+15][16]-gray_pic[i+15][15]:gray_pic[i+15][15]-gray_pic[i+15][16];
        gray_pic_dy_2[i] = (gray_pic[15][i+15]>gray_pic[16][i+15])?gray_pic[15][i+15]-gray_pic[16][i+15]:gray_pic[16][i+15]-gray_pic[15][i+15];
        sum_pic_constract_2 = sum_pic_constract_2 + gray_pic_dx_2[i] + gray_pic_dy_2[i];
    end
    sum_pic_constract_2 = (sum_pic_constract_2/4);  // 2*2
    max_constract = sum_pic_constract_2;
    GOLDEN_CONTRAST = 0;
    // $display("sum_pic_constract_2: %h", sum_pic_constract_2);

    for (i=0; i<4;i=i+1) begin
        for (j=0;j<3;j=j+1) begin
            gray_pic_dx_4[i][j] = (gray_pic[i+14][j+14]>gray_pic[i+14][j+15])? gray_pic[i+14][j+14] - gray_pic[i+14][j+15] : gray_pic[i+14][j+15] - gray_pic[i+14][j+14];
            gray_pic_dy_4[j][i] = (gray_pic[j+14][i+14]>gray_pic[j+15][i+14])? gray_pic[j+14][i+14] - gray_pic[j+15][i+14] : gray_pic[j+15][i+14] - gray_pic[j+14][i+14];

            // $display("gray_pic_dx_4[%d][%d] = %h", i, j, gray_pic_dx_4[i][j]);
            // $display("gray_pic_dy_4[%d][%d] = %h", j, i, gray_pic_dy_4[j][i]);
            sum_pic_constract_4 = sum_pic_constract_4 + gray_pic_dx_4[i][j] + gray_pic_dy_4[j][i];
        end
    end
    sum_pic_constract_4 = sum_pic_constract_4/16; // 4*4
    // $display("sum_pic_constract_4: %h", sum_pic_constract_4);

    if (sum_pic_constract_4>max_constract) begin
        max_constract = sum_pic_constract_4;
        GOLDEN_CONTRAST = 1;
    end

    for (i=0; i<6;i=i+1) begin
        for (j=0;j<5;j=j+1) begin
            gray_pic_dx_6[i][j] = (gray_pic[i+13][j+13]>gray_pic[i+13][j+14])? gray_pic[i+13][j+13] - gray_pic[i+13][j+14] : gray_pic[i+13][j+14] - gray_pic[i+13][j+13];
            gray_pic_dy_6[j][i] = (gray_pic[j+13][i+13]>gray_pic[j+14][i+13])? gray_pic[j+13][i+13] - gray_pic[j+14][i+13] : gray_pic[j+14][i+13] - gray_pic[j+13][i+13];

            sum_pic_constract_6 = sum_pic_constract_6 + (gray_pic_dx_6[i][j] + gray_pic_dy_6[j][i]);
            // $display("gray_pic_dx_6[%d][%d] = %h", i, j, gray_pic_dx_6[i][j]);
        end
    end
    sum_pic_constract_6 = sum_pic_constract_6/36;  // 6*6
    // $display("sum_pic_constract_6: %h", sum_pic_constract_6);
    if (sum_pic_constract_6>max_constract) begin
        max_constract = sum_pic_constract_6;
        GOLDEN_CONTRAST = 2;
    end

    t_initial_signal;
    t_calculate_latency;

    if (GOLDEN_CONTRAST !== out_data)
    begin
        $display("********************************\n");
        $display("\033[31mWrong Answer for function color_auto_focus!\033[0m\n");
        $display("Golden Answer: %d, Your Answer: %d\n", GOLDEN_CONTRAST, out_data);
        $display("********************************\n");
        @(negedge clk);
        $finish;
    end
    else
    begin
        $display("\033[32mPass Pattern %d, Function: color_auto_focus\033[0m", i_pat);
    end
    @(negedge clk);
end
endtask

//////////////////////////////////////////////////////////////////////

// task YOU_PASS_task; begin
//     $display("*************************************************************************");
//     $display("*                         Congratulations!                              *");
//     $display("*                Your execution cycles = %5d cycles          *", total_latency);
//     $display("*                Your clock period = %.1f ns          *", CYCLE);
//     $display("*                Total Latency = %.1f ns          *", total_latency*CYCLE);
//     $display("*************************************************************************");
//     $finish;
// end endtask

// task YOU_FAIL_task; begin
//     $display("*                              FAIL!                                    *");
//     $display("*                    Error message from PATTERN.v                       *");
// end endtask

endmodule