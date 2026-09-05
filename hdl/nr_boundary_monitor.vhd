library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- Exact boundary-integrity monitor for a 30.72 MHz reference grid.
--
-- Scope: normal cyclic prefix and numerologies mu=0,...,4.  The design does
-- not acquire synchronization from IQ samples.  It compares an externally
-- observed boundary event with the exact 3GPP-derived boundary schedule.
entity nr_boundary_monitor is
    port (
        clk                 : in  std_logic;
        rst                 : in  std_logic;
        sample_valid        : in  std_logic;
        numerology          : in  integer range 0 to 4;
        observed_boundary   : in  std_logic;
        expected_boundary   : out std_logic;
        boundary_error      : out std_logic;
        missing_boundary    : out std_logic;
        unexpected_boundary : out std_logic
    );
end entity;

architecture rtl of nr_boundary_monitor is
    constant SUBFRAME_SAMPLES : natural := 30720;
    signal sample_index : natural range 0 to SUBFRAME_SAMPLES - 1 := 0;

    function is_expected_boundary(position : natural; mu : integer) return boolean is
    begin
        case mu is
            when 0 =>
                return position = 0;
            when 1 =>
                return position = 0 or position = 15360;
            when 2 =>
                return position = 0 or position = 7688 or
                       position = 15360 or position = 23048;
            when 3 =>
                return position = 0 or position = 3852 or
                       position = 7688 or position = 11524 or
                       position = 15360 or position = 19212 or
                       position = 23048 or position = 26884;
            when 4 =>
                return position = 0 or position = 1934 or
                       position = 3852 or position = 5770 or
                       position = 7688 or position = 9606 or
                       position = 11524 or position = 13442 or
                       position = 15360 or position = 17294 or
                       position = 19212 or position = 21130 or
                       position = 23048 or position = 24966 or
                       position = 26884 or position = 28802;
            when others =>
                return false;
        end case;
    end function;
begin
    process (clk)
        variable expected_now : boolean;
    begin
        if rising_edge(clk) then
            if rst = '1' then
                sample_index        <= 0;
                expected_boundary   <= '0';
                boundary_error      <= '0';
                missing_boundary    <= '0';
                unexpected_boundary <= '0';
            elsif sample_valid = '1' then
                expected_now := is_expected_boundary(sample_index, numerology);

                if expected_now then
                    expected_boundary <= '1';
                else
                    expected_boundary <= '0';
                end if;

                if expected_now and observed_boundary = '0' then
                    missing_boundary <= '1';
                else
                    missing_boundary <= '0';
                end if;

                if (not expected_now) and observed_boundary = '1' then
                    unexpected_boundary <= '1';
                else
                    unexpected_boundary <= '0';
                end if;

                if (expected_now and observed_boundary = '0') or
                   ((not expected_now) and observed_boundary = '1') then
                    boundary_error <= '1';
                else
                    boundary_error <= '0';
                end if;

                if sample_index = SUBFRAME_SAMPLES - 1 then
                    sample_index <= 0;
                else
                    sample_index <= sample_index + 1;
                end if;
            else
                expected_boundary   <= '0';
                boundary_error      <= '0';
                missing_boundary    <= '0';
                unexpected_boundary <= '0';
            end if;
        end if;
    end process;
end architecture;

