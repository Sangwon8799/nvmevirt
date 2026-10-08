// SPDX-License-Identifier: GPL-2.0-only

#ifndef _NVMEVIRT_CONV_FTL_H
#define _NVMEVIRT_CONV_FTL_H

#include <linux/types.h>
#include <linux/bitmap.h>
#include "pqueue/pqueue.h"
#include "ssd_config.h"
#include "ssd.h"

struct convparams {
	uint32_t gc_thres_lines;
	uint32_t gc_thres_lines_high;
	bool enable_gc_delay;

	double op_area_pcent;
	int pba_pcent; /* (physical space / logical space) * 100*/
};

struct line {
	int id; /* line id, the same as corresponding block id */
	int ipc; /* invalid page count in this line */
	int vpc; /* valid page count in this line */
	struct list_head entry;
	/* position in the priority queue for victim lines */
	size_t pos;
};

/* wp: record next write addr */
struct write_pointer {
	struct line *curline;
	uint32_t ch;
	uint32_t lun;
	uint32_t pg;
	uint32_t blk;
	uint32_t pl;
};

struct line_mgmt {
	struct line *lines;

	/* free line list, we only need to maintain a list of blk numbers */
	struct list_head free_line_list;
	pqueue_t *victim_line_pq;
	struct list_head full_line_list;

	uint32_t tt_lines;
	uint32_t free_line_cnt;
	uint32_t victim_line_cnt;
	uint32_t full_line_cnt;
};

struct write_flow_control {
	uint32_t write_credits;
	uint32_t credits_to_refill;
};

struct conv_ftl {
	struct ssd *ssd;

	struct convparams cp;
	struct ppa *maptbl; /* page level mapping table */
	uint64_t *rmap; /* reverse mapptbl, assume it's stored in OOB */
	struct write_pointer wp;
	struct write_pointer gc_wp;
	struct line_mgmt lm;
	struct write_flow_control wfc;
#if KSC_GC_STATS
	/* KSC2026 statistics (only touched by the dispatcher thread) */
	uint32_t ksc_part;
	bool ksc_gc_seen;
	uint64_t ksc_host_pgs; /* mapping-unit pages written by host commands */
	uint64_t ksc_gc_pgs; /* mapping-unit pages copied by GC */
	uint64_t ksc_gc_cnt; /* victim lines cleaned */
#endif
#if KSC_WBUF_MERGE
	/* KSC2026 write-buffer merge (only touched by the dispatcher thread): one open mapping unit per
	 * partition collects host writes smaller than the mapping unit until it is full or replaced */
	uint64_t ksc_open_lpn; /* global lpn of the open mapping unit, INVALID_LPN if none */
	DECLARE_BITMAP(ksc_open_mask, MAPPING_UNIT / LBA_SIZE); /* sectors of the open unit written so far */
	uint64_t ksc_mg_open; /* units opened by a partial write */
	uint64_t ksc_mg_merge; /* writes that joined the open unit */
	uint64_t ksc_mg_full; /* open units written to flash because they became full */
	uint64_t ksc_mg_evict; /* open units written to flash partially filled (replaced by another unit) */
	uint64_t ksc_mg_direct; /* whole-unit writes that did not touch the open unit */
#endif
};

void conv_init_namespace(struct nvmev_ns *ns, uint32_t id, uint64_t size, void *mapped_addr,
			 uint32_t cpu_nr_dispatcher);

void conv_remove_namespace(struct nvmev_ns *ns);

bool conv_proc_nvme_io_cmd(struct nvmev_ns *ns, struct nvmev_request *req,
			   struct nvmev_result *ret);

#endif
