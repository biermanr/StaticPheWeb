/* spheweb shared Manhattan renderer.
 *
 * Lifted from the original single-file manhattan.html template so that every
 * phenotype page reuses ONE copy of the d3 logic instead of re-embedding it.
 * Exposes window.spheweb.renderManhattan(containerId, data), where data is the
 * legacy binned payload {variant_bins, unbinned_variants}.
 *
 * Depends on vendored d3 (v5), d3-tip and underscore (loaded before this file).
 */
(function () {
    "use strict";

    // Tooltip body (underscore template). Each field is rendered only if present,
    // so missing annotations (rsids / nearest_genes / ...) are simply omitted.
    var TOOLTIP_TEMPLATE =
        "<% if(_.has(d, 'chrom')) { %><b><%= d.chrom %>:<%= d.pos.toLocaleString() %> <%= d.ref %> / <%= d.alt %></b><br><% } %>\n" +
        "<% if(_.has(d, 'rsids')) { %><% _.each(_.filter((d.rsids||\"\").split(\",\")), function(rsid) { %>rsid: <b><%= rsid %></b><br><% }) %><% } %>\n" +
        "<% if(_.has(d, 'nearest_genes')) { %>nearest gene<%= _.contains(d.nearest_genes, \",\")? \"s\":\"\" %>: <b><%= d.nearest_genes %></b><br><% } %>\n" +
        "<% if(_.has(d, 'pval')) { %>P-value: <b><%= d['pval'] %></b><br><% } %>\n" +
        "<% if(_.has(d, 'beta')) { %>Beta: <b><%= d.beta %></b><% if(_.has(d, \"sebeta\")){ %> (se:<b><%= d.sebeta %></b>)<% } %><br><% } %>\n" +
        "<% if(_.has(d, 'maf')) { %>MAF: <b><%= d['maf'] %></b><br><% } %>\n" +
        "<% if(_.has(d, 'num_significant_in_peak') && d.num_significant_in_peak>1) { %>#significant variants in peak: <%= d.num_significant_in_peak %><br><% } %>";

    // Convenience string formatter: fmt("translate({0},{1})", x, y).
    function fmt(format) {
        var args = Array.prototype.slice.call(arguments, 1);
        return format.replace(/{(\d+)}/g, function (match, number) {
            return typeof args[number] != "undefined" ? args[number] : match;
        });
    }

    function renderManhattan(containerId, data) {
        var container = document.getElementById(containerId);
        container.innerHTML = ""; // clear any previously-rendered plot

        var variant_bins = data.variant_bins;
        // Order from weakest to strongest p-value so the strongest variant ends up
        // on top (z-order) and is easily hoverable.
        var unbinned_variants = _.sortBy(data.unbinned_variants, function (d) {
            return -d.pval;
        });

        var get_chrom_offsets = _.memoize(function () {
            var chrom_padding = 2e7;
            var chrom_extents = {};

            var update_chrom_extents = function (variant) {
                if (!(variant.chrom in chrom_extents)) {
                    chrom_extents[variant.chrom] = [variant.pos, variant.pos];
                } else if (variant.pos > chrom_extents[variant.chrom][1]) {
                    chrom_extents[variant.chrom][1] = variant.pos;
                } else if (variant.pos < chrom_extents[variant.chrom][0]) {
                    chrom_extents[variant.chrom][0] = variant.pos;
                }
            };
            variant_bins.forEach(update_chrom_extents);
            unbinned_variants.forEach(update_chrom_extents);

            var chroms = _.sortBy(Object.keys(chrom_extents), parseInt);

            var chrom_genomic_start_positions = {};
            chrom_genomic_start_positions[chroms[0]] = 0;
            for (var i = 1; i < chroms.length; i++) {
                chrom_genomic_start_positions[chroms[i]] =
                    chrom_genomic_start_positions[chroms[i - 1]] +
                    chrom_extents[chroms[i - 1]][1] -
                    chrom_extents[chroms[i - 1]][0] +
                    chrom_padding;
            }

            var chrom_offsets = {};
            Object.keys(chrom_genomic_start_positions).forEach(function (chrom) {
                chrom_offsets[chrom] =
                    chrom_genomic_start_positions[chrom] - chrom_extents[chrom][0];
            });

            return {
                chrom_extents: chrom_extents,
                chroms: chroms,
                chrom_genomic_start_positions: chrom_genomic_start_positions,
                chrom_offsets: chrom_offsets,
            };
        });

        function get_genomic_position(variant) {
            var chrom_offsets = get_chrom_offsets().chrom_offsets;
            return chrom_offsets[variant.chrom] + variant.pos;
        }

        function get_y_axis_config(max_data_qval, plot_height, includes_pval0) {
            var possible_ticks = [];
            if (max_data_qval <= 14) {
                possible_ticks = _.range(0, 14.1, 2);
            } else if (max_data_qval <= 28) {
                possible_ticks = _.range(0, 28.1, 4);
            } else if (max_data_qval <= 40) {
                possible_ticks = _.range(0, 40.1, 8);
            } else {
                possible_ticks = _.range(0, 20.1, 4);
                if (max_data_qval <= 70) {
                    possible_ticks = possible_ticks.concat([30, 40, 50, 60, 70]);
                } else if (max_data_qval <= 120) {
                    possible_ticks = possible_ticks.concat([40, 60, 80, 100, 120]);
                } else if (max_data_qval <= 220) {
                    possible_ticks = possible_ticks.concat([60, 100, 140, 180, 220]);
                } else {
                    var power_of_ten = Math.pow(
                        10,
                        Math.floor(Math.log10(max_data_qval))
                    );
                    var first_digit = max_data_qval / power_of_ten;
                    var multipliers;
                    if (first_digit <= 2) {
                        multipliers = [0.5, 1, 1.5, 2];
                    } else if (first_digit <= 4) {
                        multipliers = [1, 2, 3, 4];
                    } else {
                        multipliers = [2, 4, 6, 8, 10];
                    }
                    possible_ticks = possible_ticks.concat(
                        multipliers.map(function (m) {
                            return m * power_of_ten;
                        })
                    );
                }
            }
            // Include all ticks < qval, then also the next tick, so the largest
            // tick is always >= the largest variant.
            var ticks = possible_ticks.filter(function (qval) {
                return qval < max_data_qval;
            });
            if (ticks.length < possible_ticks.length) {
                ticks.push(possible_ticks[ticks.length]);
            }

            var max_plot_qval = ticks[ticks.length - 1];
            if (includes_pval0) {
                max_plot_qval *= 1.1;
            }
            var scale = d3.scaleLinear().clamp(true);
            if (max_plot_qval <= 40) {
                scale = scale.domain([max_plot_qval, 0]).range([0, plot_height]);
            } else {
                scale = scale
                    .domain([max_plot_qval, 20, 0])
                    .range([0, plot_height / 2, plot_height]);
            }

            if (includes_pval0) {
                ticks.push(Infinity);
            }

            return {
                scale: scale,
                draw_break_at_20: !(max_plot_qval <= 40),
                ticks: ticks,
            };
        }

        // Setup plot dimensions
        var svg_width = container.clientWidth || 1000;
        var svg_height = 550;

        var plot_margin = { left: 70, right: 30, top: 20, bottom: 50 };

        var plot_width = svg_width - plot_margin.left - plot_margin.right;
        var plot_height = svg_height - plot_margin.top - plot_margin.bottom;

        var gwas_svg = d3
            .select(container)
            .append("svg")
            .attr("id", "gwas_svg")
            .attr("width", svg_width)
            .attr("height", svg_height)
            .style("display", "block")
            .style("margin", "auto");

        var gwas_plot = gwas_svg
            .append("g")
            .attr("id", "gwas_plot")
            .attr(
                "transform",
                fmt("translate({0},{1})", plot_margin.left, plot_margin.top)
            );

        var significance_threshold = 5e-8;

        var genomic_position_extent = (function () {
            var extent1 = d3.extent(variant_bins, get_genomic_position);
            var extent2 = d3.extent(unbinned_variants, get_genomic_position);
            return d3.extent(extent1.concat(extent2));
        })();

        var x_scale = d3
            .scaleLinear()
            .domain(genomic_position_extent)
            .range([0, plot_width]);

        var includes_pval0 = _.any(unbinned_variants, function (variant) {
            return variant.pval === 0;
        });

        var highest_plot_qval = Math.max(
            -Math.log10(significance_threshold) + 0.5,
            (function () {
                var best_unbinned_qval = -Math.log10(
                    d3.min(unbinned_variants, function (d) {
                        return d.pval === 0 ? 1 : d.pval;
                    })
                );
                if (best_unbinned_qval !== undefined) return best_unbinned_qval;
                return d3.max(variant_bins, function (bin) {
                    return d3.max(bin, _.property("qval"));
                });
            })()
        );

        var y_axis_config = get_y_axis_config(
            highest_plot_qval,
            plot_height,
            includes_pval0
        );
        var y_scale = y_axis_config.scale;

        var y_axis = d3
            .axisLeft(y_scale)
            .tickFormat(d3.format("d"))
            .tickValues(y_axis_config.ticks);

        gwas_plot
            .append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(-8,0)")
            .call(y_axis);

        if (includes_pval0) {
            var y_axis_break_inf_offset =
                y_scale(Infinity) + (y_scale(0) - y_scale(Infinity)) * 0.03;
            gwas_plot
                .append("line")
                .attr("x1", -8 - 7)
                .attr("x2", -8 + 7)
                .attr("y1", y_axis_break_inf_offset + 6)
                .attr("y2", y_axis_break_inf_offset - 6)
                .attr("stroke", "#666")
                .attr("stroke-width", "3px");
        }

        if (y_axis_config.draw_break_at_20) {
            var y_axis_break_20_offset = y_scale(20);
            gwas_plot
                .append("line")
                .attr("x1", -8 - 7)
                .attr("x2", -8 + 7)
                .attr("y1", y_axis_break_20_offset + 6)
                .attr("y2", y_axis_break_20_offset - 6)
                .attr("stroke", "#666")
                .attr("stroke-width", "3px");
        }

        gwas_svg
            .append("text")
            .style("text-anchor", "middle")
            .attr(
                "transform",
                fmt(
                    "translate({0},{1})rotate(-90)",
                    plot_margin.left * 0.4,
                    plot_height / 2 + plot_margin.top
                )
            )
            .text("-log₁₀(p-value)");

        var color_by_chrom = d3
            .scaleOrdinal()
            .domain(get_chrom_offsets().chroms)
            .range(["rgb(120,120,186)", "rgb(0,66,66)"]);

        var chroms_and_midpoints = (function () {
            var v = get_chrom_offsets();
            return v.chroms.map(function (chrom) {
                return {
                    chrom: chrom,
                    midpoint:
                        v.chrom_genomic_start_positions[chrom] +
                        (v.chrom_extents[chrom][1] - v.chrom_extents[chrom][0]) / 2,
                };
            });
        })();

        gwas_svg
            .selectAll("text.chrom_label")
            .data(chroms_and_midpoints)
            .enter()
            .append("text")
            .style("text-anchor", "middle")
            .attr("transform", function (d) {
                return fmt(
                    "translate({0},{1})",
                    plot_margin.left + x_scale(d.midpoint),
                    plot_height + plot_margin.top + 20
                );
            })
            .text(function (d) {
                return d.chrom;
            })
            .style("fill", function (d) {
                return color_by_chrom(d.chrom);
            });

        gwas_plot
            .append("line")
            .attr("x1", 0)
            .attr("x2", plot_width)
            .attr("y1", y_scale(-Math.log10(significance_threshold)))
            .attr("y2", y_scale(-Math.log10(significance_threshold)))
            .attr("stroke-width", "5px")
            .attr("stroke", "lightgray")
            .attr("stroke-dasharray", "10,10");

        var tooltip_template = _.template(TOOLTIP_TEMPLATE);

        var point_tooltip = d3
            .tip()
            .attr("class", "d3-tip")
            .html(function (d) {
                return tooltip_template({ d: d });
            })
            .offset([-6, 0]);

        gwas_svg.call(point_tooltip);

        // Gene labels for the strongest peaks. Skipped entirely when the input
        // carries no nearest_genes annotation (raw GWAS, the v1 case).
        var variants_to_label = _.sortBy(
            _.where(unbinned_variants, { peak: true }),
            _.property("pval")
        )
            .filter(function (d) {
                return d.pval < 5e-8 && d.nearest_genes;
            })
            .slice(0, 7);
        gwas_plot
            .append("g")
            .attr("class", "genenames")
            .selectAll("text.genenames")
            .data(variants_to_label)
            .enter()
            .append("text")
            .attr("class", "genename_text")
            .style("font-style", "italic")
            .attr("text-anchor", "middle")
            .attr("transform", function (d) {
                return fmt(
                    "translate({0},{1})",
                    x_scale(get_genomic_position(d)),
                    y_scale(-Math.log10(d.pval)) - 5
                );
            })
            .text(function (d) {
                if (d.nearest_genes.split(",").length <= 2) {
                    return d.nearest_genes;
                }
                return d.nearest_genes.split(",").slice(0, 2).join(",") + ",...";
            });

        gwas_plot
            .append("g")
            .attr("class", "variant_points")
            .selectAll("circle.variant_point")
            .data(unbinned_variants)
            .enter()
            .append("circle")
            .attr("class", "variant_point")
            .attr("id", function (d) {
                return fmt("variant-point-{0}-{1}-{2}-{3}", d.chrom, d.pos, d.ref, d.alt);
            })
            .attr("cx", function (d) {
                return x_scale(get_genomic_position(d));
            })
            .attr("cy", function (d) {
                return y_scale(-Math.log10(d.pval));
            })
            .attr("r", 2.3)
            .style("fill", function (d) {
                return color_by_chrom(d.chrom);
            })
            .on("mouseover", function (d) {
                point_tooltip.show(d, this);
            })
            .on("mouseout", point_tooltip.hide);

        var bins = gwas_plot
            .append("g")
            .attr("class", "bins")
            .selectAll("g.bin")
            .data(variant_bins)
            .enter()
            .append("g")
            .attr("class", "bin")
            .attr("data-index", function (d, i) {
                return i;
            })
            .each(function (d) {
                d.x = x_scale(get_genomic_position(d));
                d.color = color_by_chrom(d.chrom);
            });

        bins.selectAll("circle.binned_variant_point")
            .data(_.property("qvals"))
            .enter()
            .append("circle")
            .attr("class", "binned_variant_point")
            .attr("cx", function () {
                var parent_i = +this.parentNode.getAttribute("data-index");
                return variant_bins[parent_i].x;
            })
            .attr("cy", function (qval) {
                return y_scale(qval);
            })
            .attr("r", 2.3)
            .style("fill", function () {
                var parent_i = +this.parentNode.getAttribute("data-index");
                return variant_bins[parent_i].color;
            });

        bins.selectAll("line.binned_variant_line")
            .data(_.property("qval_extents"))
            .enter()
            .append("line")
            .attr("class", "binned_variant_line")
            .attr("x1", function () {
                var parent_i = +this.parentNode.getAttribute("data-index");
                return variant_bins[parent_i].x;
            })
            .attr("x2", function () {
                var parent_i = +this.parentNode.getAttribute("data-index");
                return variant_bins[parent_i].x;
            })
            .attr("y1", function (d) {
                return y_scale(d[0]);
            })
            .attr("y2", function (d) {
                return y_scale(d[1]);
            })
            .style("stroke", function () {
                var parent_i = +this.parentNode.getAttribute("data-index");
                return variant_bins[parent_i].color;
            })
            .style("stroke-width", 4.6)
            .style("stroke-linecap", "round");
    }

    window.spheweb = { renderManhattan: renderManhattan };
})();
