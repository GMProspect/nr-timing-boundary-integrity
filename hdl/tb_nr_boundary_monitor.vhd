library ieee;
use ieee.std_logic_1164.all;
use std.env.all;

entity tb_nr_boundary_monitor is
end entity;

architecture test of tb_nr_boundary_monitor is
    constant CLK_PERIOD : time := 10 ns;
    signal clk                 : std_logic := '0';
    signal rst                 : std_logic := '1';
    signal sample_valid        : std_logic := '0';
    signal numerology          : integer range 0 to 4 := 2;
    signal observed_boundary   : std_logic := '0';
    signal expected_boundary   : std_logic;
    signal boundary_error      : std_logic;
    signal missing_boundary    : std_logic;
    signal unexpected_boundary : std_logic;

    function is_mu2_boundary(position : natural) return boolean is
    begin
        return position = 0 or position = 7688 or
               position = 15360 or position = 23048;
    end function;
begin
    clk <= not clk after CLK_PERIOD / 2;

    dut : entity work.nr_boundary_monitor
        port map (
            clk                 => clk,
            rst                 => rst,
            sample_valid        => sample_valid,
            numerology          => numerology,
            observed_boundary   => observed_boundary,
            expected_boundary   => expected_boundary,
            boundary_error      => boundary_error,
            missing_boundary    => missing_boundary,
            unexpected_boundary => unexpected_boundary
        );

    stimulus : process
    begin
        wait until rising_edge(clk);
        rst <= '0';
        sample_valid <= '1';

        -- One complete, correctly observed mu=2 subframe.
        for position in 0 to 30719 loop
            if is_mu2_boundary(position) then
                observed_boundary <= '1';
            else
                observed_boundary <= '0';
            end if;
            wait until rising_edge(clk);
            wait for 1 ns;
            assert boundary_error = '0'
                report "false boundary error during aligned schedule" severity failure;
        end loop;

        -- Reset and inject an unexpected event at sample 10.
        rst <= '1';
        sample_valid <= '0';
        wait until rising_edge(clk);
        rst <= '0';
        sample_valid <= '1';
        for position in 0 to 10 loop
            if position = 0 or position = 10 then
                observed_boundary <= '1';
            else
                observed_boundary <= '0';
            end if;
            wait until rising_edge(clk);
            wait for 1 ns;
        end loop;
        assert unexpected_boundary = '1' and boundary_error = '1'
            report "unexpected boundary was not detected" severity failure;

        -- Reset and omit the expected event at sample 7688.
        rst <= '1';
        sample_valid <= '0';
        wait until rising_edge(clk);
        rst <= '0';
        sample_valid <= '1';
        for position in 0 to 7688 loop
            if position = 0 then
                observed_boundary <= '1';
            else
                observed_boundary <= '0';
            end if;
            wait until rising_edge(clk);
            wait for 1 ns;
        end loop;
        assert missing_boundary = '1' and boundary_error = '1'
            report "missing boundary was not detected" severity failure;

        report "all nr_boundary_monitor tests passed" severity note;
        stop;
        wait;
    end process;
end architecture;

